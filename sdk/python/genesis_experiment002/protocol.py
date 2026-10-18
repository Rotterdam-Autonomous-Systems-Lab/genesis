"""Fixed EIP-712 schemas and strict public-message codec. No private-key I/O."""

import json
import os
import stat
import re
import time

from eth_account import Account
from eth_account.messages import encode_typed_data
from web3 import Web3

LIMIT = 16384
MAX_PRICE = 10**15
PRICE = 10**12
SERVICE = Web3.to_hex(Web3.keccak(text="genesis.sum-u64.v1"))
POLICY = Web3.to_hex(Web3.keccak(text="genesis.exp002.direct-sum-u64.v1"))
SCHEMAS = {
    "Advertisement": "address provider,bytes32 serviceId,bytes32 policyId,uint256 price,uint64 offerExpiresAt,bytes32 runId",
    "Terms": "address requester,address provider,bytes32 serviceId,bytes32 policyId,uint64 x,uint64 y,uint256 price,uint64 fundBefore,uint64 claimBefore,bytes32 salt,bytes32 runId",
    "Authorization": "address requester,address provider,bytes32 agreementId,uint256 nonce,uint256 maxAmount,uint64 expiresAt,bytes32 runId",
    "Claim": "address requester,address provider,bytes32 agreementId,uint256 authorizationNonce,uint256 value,bytes32 runId",
}
TYPES = {
    name: [dict(zip(("type", "name"), field.split())) for field in fields.split(",")]
    for name, fields in SCHEMAS.items()
}


class Rejected(Exception):
    """Untrusted input or local policy rejected; never carries secret material."""


class Inconclusive(Exception):
    """Environment/chain evidence unavailable; never claim settlement success."""


def exact(value, fields):
    if not isinstance(value, dict) or set(value) != set(fields):
        raise Rejected("unexpected fields")
    return value


def integer(value, bits=256):
    if (
        not isinstance(value, str)
        or len(value) > 78
        or not re.fullmatch(r"0|[1-9][0-9]*", value)
    ):
        raise Rejected("noncanonical integer")
    result = int(value)
    if result >= 2**bits:
        raise Rejected("integer range")
    return result


def hex_value(value, length):
    if not isinstance(value, str) or not re.fullmatch(
        r"0x[0-9a-f]{" + str(length * 2) + "}", value
    ):
        raise Rejected("invalid hex width")
    return value.lower()


def duplicate_check(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Rejected("duplicate key")
        result[key] = value
    return result


def decode(raw):
    if len(raw) > LIMIT:
        raise Rejected("message too large")
    try:
        return json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=duplicate_check,
            parse_constant=lambda _: (_ for _ in ()).throw(Rejected("constant")),
        )
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise Rejected("invalid JSON") from exc


def encode(value):
    raw = json.dumps(
        value, sort_keys=True, allow_nan=False, separators=(",", ":"), ensure_ascii=True
    ).encode()
    if len(raw) > LIMIT:
        raise Rejected("message too large")
    return raw


def read(path):
    # Check the opened descriptor, not an earlier pathname lookup. O_NONBLOCK
    # prevents an untrusted FIFO from defeating the agent timeout.
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > LIMIT:
                raise Rejected("nonregular/oversized transport")
            return decode(stream.read(LIMIT + 1))
    except OSError as exc:
        raise Rejected("unreadable transport") from exc


def write(path, value):
    # Atomic no-clobber publication. A competing writer may deny availability,
    # but cannot cause a previously published message to be silently replaced.
    if path.exists() or path.is_symlink():
        raise Rejected("message already exists")
    temp = path.with_suffix(".tmp")
    owned = False
    try:
        with temp.open("xb") as stream:
            owned = True
            stream.write(encode(value))
        os.link(temp, path)
    except OSError as exc:
        raise Rejected("transport publication failed") from exc
    finally:
        if owned:
            temp.unlink(missing_ok=True)


def wait(path, end):
    while time.monotonic() < end:
        if path.exists():
            return read(path)
        time.sleep(0.025)
    raise Inconclusive("transport timeout")


def normalize(kind, message):
    exact(message, [f["name"] for f in TYPES[kind]])
    parsed = {}
    for field in TYPES[kind]:
        name, typ = field["name"], field["type"]
        value = message[name]
        if typ.startswith("uint"):
            parsed[name] = integer(value, int(typ[4:]))
        elif typ == "address":
            parsed[name] = Web3.to_checksum_address(hex_value(value, 20))
        else:
            parsed[name] = hex_value(value, 32)
    return parsed


def wire(kind, **values):
    result = {
        field["name"]: (
            str(values[field["name"]])
            if field["type"].startswith("uint")
            else values[field["name"]].lower()
        )
        for field in TYPES[kind]
    }
    normalize(kind, result)
    return result


class Signing:
    def __init__(self, contract, run_id):
        self.domain = {
            "name": "GenesisExperiment002",
            "version": "1",
            "chainId": "31337",
            "verifyingContract": Web3.to_checksum_address(hex_value(contract, 20)),
        }
        self.run_id = hex_value(run_id, 32)

    def typed(self, kind, message):
        parsed = normalize(kind, message)
        if parsed["runId"] != self.run_id:
            raise Rejected("wrong run")
        return encode_typed_data(
            domain_data=self.domain,
            message_types={kind: TYPES[kind]},
            message_data=parsed,
        )

    def digest(self, kind, message):
        typed = self.typed(kind, message)
        return Web3.to_hex(
            Web3.keccak(b"\x19" + typed.version + typed.header + typed.body)
        )

    def sign(self, account, kind, message):
        return Web3.to_hex(account.sign_message(self.typed(kind, message)).signature)

    def verify(self, kind, message, signature, signer):
        data = bytes.fromhex(hex_value(signature, 65)[2:])
        # Match OpenZeppelin's supported Ethereum encoding (not custom crypto).
        if (
            not 0
            < int.from_bytes(data[:32], "big")
            < int(
                "fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141", 16
            )
            or data[64] not in (27, 28)
            or not 0
            < int.from_bytes(data[32:64], "big")
            <= int(
                "7fffffffffffffffffffffffffffffff5d576e7357a4501ddfe92f46681b20a0", 16
            )
        ):
            raise Rejected("unsupported signature")
        try:
            recovered = Account.recover_message(
                self.typed(kind, message), signature=signature
            )
        except (ValueError, TypeError) as exc:
            raise Rejected("bad signature") from exc
        if recovered.lower() != hex_value(signer.lower(), 20):
            raise Rejected("wrong signer")

    def envelope(self, kind, message, signatures):
        return {"kind": kind, "message": message, "signatures": signatures}

    def open(self, envelope, kind, parties):
        exact(envelope, ("kind", "message", "signatures"))
        if envelope["kind"] != kind:
            raise Rejected("wrong kind")
        primary = "Terms" if kind == "termsProposal" else kind.capitalize()
        exact(envelope["signatures"], parties)
        for role, signer in parties.items():
            self.verify(
                primary, envelope["message"], envelope["signatures"][role], signer
            )
        return normalize(primary, envelope["message"])


def tuple_for(kind, message):
    parsed = normalize(kind, message)
    return tuple(parsed[f["name"]] for f in TYPES[kind])


def check_terms(message, requester, provider, now):
    t = normalize("Terms", message)
    if (
        t["requester"].lower() != requester.lower()
        or t["provider"].lower() != provider.lower()
        or requester.lower() == provider.lower()
        or int(requester, 16) == 0
        or int(provider, 16) == 0
        or t["serviceId"] != SERVICE
        or t["policyId"] != POLICY
        or not 0 < t["price"] <= MAX_PRICE
        or not now < t["fundBefore"] < t["claimBefore"]
    ):
        raise Rejected("terms policy")
    return t
