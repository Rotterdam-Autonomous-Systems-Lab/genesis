"""Shared codec/crypto and pure admission checks; no ledger mutation."""
import copy
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from Crypto.Signature import eddsa

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('frozen_codec', ROOT/'research/fixtures/native_l1/validate.py')
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)
DOMAIN = codec.DOMAIN
ZERO = bytes(32)


def packed(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(codec.encode(value)).hexdigest()


class Reject(Exception):
    pass


class Context:
    def __init__(self, manifest):
        # Deliberately exclude all vector expectations from the candidate context.
        self.manifest = {k: copy.deepcopy(manifest[k]) for k in ('actors','aliases','terms','network_id','service_id')}
        self.actors = {bytes.fromhex(a['id']): n for n,a in self.manifest['actors'].items()}
        self.aliases = {kind: {bytes.fromhex(v): n for n,v in table.items()} for kind,table in self.manifest['aliases'].items()}
        self.term_names={v['agreement_id']:k for k,v in self.manifest['terms'].items()}
        self.metrics = Counter()

    def actor(self, raw):
        if raw not in self.actors:
            raise Reject('reject:authority')
        return self.actors[raw]

    def alias(self, kind, raw):
        return self.aliases[kind].get(raw, raw.hex())

    def verify(self, actor, signature, raw_digest):
        self.metrics['signatures'] += 1
        try:
            key = eddsa.import_public_key(bytes.fromhex(self.manifest['actors'][actor]['public_key']))
            eddsa.new(key, 'rfc8032').verify(raw_digest, signature)
        except (ValueError, TypeError):
            raise Reject('reject:signature') from None

    def parse(self, intent):
        raw = bytes.fromhex(intent['preimage_hex'])
        self.metrics['parsed_bytes'] += len(raw)
        self.metrics['hashed_bytes'] += len(raw)
        try:
            domain, u = codec.decode(raw)
            if domain != DOMAIN or len(u) != 9 or u[0] != 1:
                raise ValueError('header')
            _, network, actor_id, epoch, sequence, expiry, ceiling, op, args = u
            if any(type(x) is not int or not 0 <= x <= 2**64-1 for x in (epoch,sequence,expiry,ceiling,op)):
                raise ValueError('integer')
            if not isinstance(args,list) or op not in range(1,10):
                raise ValueError('operation')
            if len(actor_id) != 32 or len(network) != 32:
                raise ValueError('identity')
            # Exact argument lengths/types; no field in descriptive JSON grants authority.
            lengths = {1:4 if args[0] == ZERO else 5,2:7,3:2,4:3,5:5,6:2,7:1,8:1,9:1}
            if len(args) != lengths[op]:
                raise ValueError('arguments')
            if type(args[0]) is not bytes or len(args[0]) != 32:
                raise ValueError('target')
            if op == 6 and (type(args[1]) is not bytes or len(args[1]) != 16):
                raise ValueError('result width')
            if op == 1:
                to,amount,invoice = args[-3:]
                if type(to) is not bytes or len(to)!=32 or type(invoice) is not bytes or len(invoice)!=32 or type(amount) is not int or amount <= 0:
                    raise ValueError('transfer')
            if op in (2,4):
                delegates = args[1] if op==2 else args[2]
                if not 1 <= len(delegates) <= 32 or delegates != sorted(delegates) or len({x[0] for x in delegates}) != len(delegates):
                    raise ValueError('delegates')
                for a,e in delegates:
                    self.actor(a)
                    if type(e) is not int or e != 0:
                        raise ValueError('delegate epoch outside v1')
            if op == 2:
                for values,limit in ((args[2],8),(args[3],8)):
                    if len(values)>limit or values!=sorted(set(values)):
                        raise ValueError('scope')
                if not set(args[2]) <= {1,5} or any(type(x) is not int for x in args[4:]):
                    raise ValueError('scope/budget')
            self.metrics['decodes'] += 1
            return dict(u=u,actor=self.actor(actor_id),epoch=epoch,sequence=sequence,expiry=expiry,ceiling=ceiling,op=op,args=args,id=hashlib.sha256(raw).hexdigest())
        except (ValueError,TypeError,IndexError):
            raise Reject('reject:encoding') from None

    def authenticate(self, p, intent, read, tick):
        """Pure checks only; native stores supply read access and enforce atomic commit."""
        actor,op,a = p['actor'],p['op'],p['args']
        if p['u'][1].hex() != self.manifest['network_id']:
            raise Reject('reject:network')
        if p['epoch'] != read('epochs',actor):
            raise Reject('reject:key_epoch')
        self.verify(actor,bytes.fromhex(intent['signature']),bytes.fromhex(p['id']))
        prior = read('consumed',actor+':'+str(p['sequence']))
        if prior:
            raise Reject('duplicate' if prior['intent_id'] == p['id'] else 'reject:sequence_conflict')
        if tick >= p['expiry']:
            raise Reject('reject:intent_expired')
        g = None
        if op in (1,5) and a[0] != ZERO:
            name = self.alias('grants',a[0]); g=read('grants',name)
            if not g:
                raise Reject('reject:authority')
            if a[1] != g['version']:
                raise Reject('reject:grant_version')
            if g['status'] != 'active':
                raise Reject('reject:grant_revoked')
            if g['owner_epoch'] != read('epochs',g['owner']) or actor not in g['delegates']:
                raise Reject('reject:authority')
            recipient = self.actor(a[-3] if op==1 else a[2][2])
            if op not in g['actions'] or recipient not in g['recipients']:
                raise Reject('reject:scope')
            if tick >= g['expires']:
                raise Reject('reject:grant_expired')
            p['grant'] = name
        elif op in (3,4,9):
            name=self.alias('grants',a[0]); target=read('grants',name)
            if not target or target['owner'] != actor:
                raise Reject('reject:authority')
            if op in (3,4) and a[1] != target['version']:
                raise Reject('reject:grant_version')
        elif op in (6,7):
            target=read('agreements',self.alias('agreements',a[0]))
            if not target or target['provider' if op==6 else 'requester'] != actor:
                raise Reject('reject:authority')
        elif op==8:
            target=read('credits',self.alias('credits',a[0]))
            if not target or target['owner'] != actor:
                raise Reject('reject:authority')
        if op==5:
            t=a[2]
            if len(t)!=10 or t[0].hex()!=self.manifest['network_id'] or t[4].hex()!=self.manifest['service_id']:
                raise Reject('reject:terms')
            requester,provider=self.actor(t[1]),self.actor(t[2])
            if requester==provider or t[7]<=0 or t[8]>=t[9] or (g and g['owner']!=requester) or (not g and actor!=requester):
                raise Reject('reject:authority')
            h=bytes.fromhex(digest([DOMAIN,5,t])); self.metrics['hashed_bytes'] += len(codec.encode([DOMAIN,5,t]))
            self.verify(requester,a[3],h); self.verify(provider,a[4],h)
        reserve = g['fee_pool'] if g else read('balances',actor)
        if p['ceiling'] < 1 or reserve < p['ceiling']:
            raise Reject('reject:fee_budget')

    def terms_record(self, t):
        # Stateless conversion, no mutation or computed state deltas.
        name=self.alias('agreements',bytes.fromhex(digest([DOMAIN,5,t])))
        term_name=self.term_names.get(digest([DOMAIN,5,t]),name)
        return name, dict(requester=self.actor(t[1]),provider=self.actor(t[2]),price=t[7],fund_before=t[8],claim_before=t[9],state='Funded',result=0,terms=term_name)
