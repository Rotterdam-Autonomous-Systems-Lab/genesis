"""Validate frozen data/encodings/accounting; never apply candidate transitions."""
import hashlib
import json
import re
from pathlib import Path
from Crypto.Signature import eddsa

ROOT = Path(__file__).resolve().parent
DOMAIN = bytes.fromhex('47454e455349532d4c41422d303137')
U64 = 2**64 - 1


def load_json(path):
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError('duplicate JSON key')
            out[k] = v
        return out
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('constant')))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_schema(value, spec, root, where='$'):
    """Small explicit subset used by schema.json; no general JSON Schema claim."""
    if '$ref' in spec:
        return check_schema(value, root['$defs'][spec['$ref'].split('/')[-1]], root, where)
    typ = spec.get('type')
    types = {'object': dict, 'array': list, 'string': str, 'integer': int, 'boolean': bool}
    if typ:
        require(type(value) is types[typ], where + ': type')
    if 'enum' in spec:
        require(value in spec['enum'], where + ': enum')
    if typ == 'object':
        props = spec.get('properties', {})
        require(set(spec.get('required', [])) <= set(value), where + ': required')
        for key, item in value.items():
            sub = props.get(key, spec.get('additionalProperties', {}))
            require(sub is not False, where + ': unknown field ' + key)
            if isinstance(sub, dict):
                check_schema(item, sub, root, where + '.' + key)
    if typ == 'array':
        require(spec.get('minItems', 0) <= len(value) <= spec.get('maxItems', 100000), where + ': length')
        if spec.get('uniqueItems'):
            require(len({json.dumps(v, sort_keys=True) for v in value}) == len(value), where + ': duplicate')
        for i, item in enumerate(value):
            check_schema(item, spec.get('items', {}), root, where + '[' + str(i) + ']')
    if typ == 'string' and 'pattern' in spec:
        require(re.fullmatch(spec['pattern'], value) is not None, where + ': pattern')
    if typ == 'integer':
        require(spec.get('minimum', 0) <= value <= spec.get('maximum', U64), where + ': integer range')


def unpack(value):
    if type(value) is dict:
        require(set(value) == {'bytes'}, 'portable bytes fields')
        require(type(value['bytes']) is str and re.fullmatch(r'(?:[0-9a-f]{2})*', value['bytes']), 'hex')
        return bytes.fromhex(value['bytes'])
    if type(value) is list:
        return [unpack(v) for v in value]
    require(type(value) is int and 0 <= value <= U64, 'CBOR profile type/range')
    return value


def encode(value, depth=0):
    require(depth <= 8, 'CBOR depth')
    def head(major, size):
        require(0 <= size <= U64, 'CBOR range')
        if size < 24:
            return bytes([major * 32 + size])
        for tag, width in ((24, 1), (25, 2), (26, 4), (27, 8)):
            if size < 2**(8 * width):
                return bytes([major * 32 + tag]) + size.to_bytes(width, 'big')
    if type(value) is int:
        return head(0, value)
    if type(value) is bytes:
        return head(2, len(value)) + value
    if type(value) is list:
        return head(4, len(value)) + b''.join(encode(v, depth+1) for v in value)
    raise ValueError('CBOR profile type')


def decode(raw):
    """Independent parsing path with complete consumption and canonical re-encode."""
    def item(pos, depth):
        require(depth <= 8 and pos < len(raw), 'truncated/deep CBOR')
        first = raw[pos]; pos += 1
        major, ai = divmod(first, 32)
        require(major in (0, 2, 4) and ai <= 27, 'CBOR profile')
        if ai < 24:
            size = ai
        else:
            width = {24: 1, 25: 2, 26: 4, 27: 8}[ai]
            require(pos + width <= len(raw), 'truncated CBOR argument')
            size = int.from_bytes(raw[pos:pos+width], 'big'); pos += width
        if major == 0:
            return size, pos
        if major == 2:
            require(pos+size <= len(raw), 'truncated bytes')
            return raw[pos:pos+size], pos+size
        require(size <= len(raw)-pos, 'oversized array')
        values = []
        for _ in range(size):
            value, pos = item(pos, depth+1); values.append(value)
        return values, pos
    require(len(raw) <= 16384, 'CBOR input ceiling')
    value, end = item(0, 0)
    require(end == len(raw) and encode(value) == raw, 'trailing/noncanonical CBOR')
    return value


def validate_snapshot(s, corpus, supply):
    require(set(s['balances']) == set(corpus['actors']) == set(s['epochs']), 'principal attribution')
    total = sum(s['balances'].values()) + s['fee_sink']
    for name, g in s['grants'].items():
        require(name in corpus['aliases']['grants'], 'grant alias')
        require(g['owner'] in corpus['actors'], 'grant owner')
        require(set(g['delegates']) <= set(corpus['actors']), 'delegate owner')
        require(set(g['recipients']) <= set(corpus['actors']), 'recipient owner')
        require(g['principal_used'] + g['principal_pool'] + g['principal_returned'] == g['principal_cap'], 'principal budget identity')
        require(g['fee_used'] + g['fee_pool'] + g['fee_returned'] == g['fee_cap'], 'fee budget identity')
        if g['status'] == 'returned':
            require(g['principal_pool'] == g['fee_pool'] == 0, 'returned pools')
        total += g['principal_pool'] + g['fee_pool']
    for name, a in s['agreements'].items():
        require(name in corpus['aliases']['agreements'] and a['terms'] in corpus['terms'], 'agreement binding')
        t = unpack(corpus['terms'][a['terms']]['array'])
        require(corpus['actors'][a['requester']]['id'] == t[1].hex() and corpus['actors'][a['provider']]['id'] == t[2].hex(), 'agreement parties')
        require((a['price'], a['fund_before'], a['claim_before']) == (t[7], t[8], t[9]), 'immutable terms')
        if a['state'] == 'Funded':
            total += a['price']
        require(a['result'] == (t[5]+t[6] if a['state'] == 'Settled' else 0), 'terminal result')
        if a['state'] in ('Settled', 'Refunded'):
            credits = [c for c in s['credits'].values() if c['agreement'] == name]
            owner = a['provider'] if a['state'] == 'Settled' else a['requester']
            require(len(credits) == 1 and credits[0]['owner'] == owner and credits[0]['amount'] == a['price'], 'terminal credit owner')
    for name, c in s['credits'].items():
        require(name in corpus['aliases']['credits'] and c['owner'] in corpus['actors'], 'credit attribution')
        a = s['agreements'].get(c['agreement'])
        require(a is not None and a['state'] in ('Settled', 'Refunded'), 'credit terminal state')
        if c['status'] == 'outstanding':
            total += c['amount']
    for key, result in s['consumed'].items():
        require(result['intent'] in corpus['intents'], 'consumed intent')
        u = unpack(corpus['intents'][result['intent']]['unsigned'])
        actor = next(n for n,v in corpus['actors'].items() if v['id'] == u[2].hex())
        require(key == actor + ':' + str(u[4]), 'consumed sequence binding')
    require(total == supply, 'supply conservation')


def validate(data=None, directory=ROOT/'v1', check_hash=True):
    directory = Path(directory)
    if data is None:
        data = load_json(directory/'corpus.json')
    if check_hash:
        names = []
        for line in (directory/'checksums.sha256').read_text().splitlines():
            digest, name = line.split()
            names.append(name)
            require(name in ('corpus.json','schema.json','codec_vectors.json','stress_plan.json'), 'checksum path')
            require(hashlib.sha256((directory/name).read_bytes()).hexdigest() == digest, 'artifact hash '+name)
        require(sorted(names) == ['codec_vectors.json','corpus.json','schema.json','stress_plan.json'], 'checksum coverage')
        expected = (directory/'corpus.sha256').read_text().split()[0]
        require(hashlib.sha256((directory/'corpus.json').read_bytes()).hexdigest() == expected, 'corpus hash')
    schema = load_json(directory/'schema.json')
    check_schema(data, schema, schema)
    require(data['lab_domain_hex'] == DOMAIN.hex(), 'lab domain')
    require(hashlib.sha256(data['genesis_header_utf8'].encode()).hexdigest() == data['network_id'], 'genesis header')
    require(len({a['id'] for a in data['actors'].values()}) == len(data['actors']), 'actor ID uniqueness')
    for label, intent in data['intents'].items():
        u = unpack(intent['unsigned']); raw = bytes.fromhex(intent['preimage_hex'])
        require(decode(raw) == [DOMAIN, u], 'wire preimage '+label)
        digest = hashlib.sha256(raw).digest()
        require(digest.hex() == intent['intent_id'], 'intent digest '+label)
        require(len(u) == 9 and u[0] == 1 and all(type(u[i]) is int for i in (0,3,4,5,6,7)), 'intent core')
        require(all(type(u[i]) is bytes and len(u[i]) == 32 for i in (1,2)), 'intent identity')
        require(u[7] in data['scope']['operations'], 'operation scope')
        signature = bytes.fromhex(intent['signature'])
        key = eddsa.import_public_key(bytes.fromhex(data['actors'][intent['signer']]['public_key']))
        eddsa.new(key, 'rfc8032').verify(digest, signature)
    for name, terms in data['terms'].items():
        t = unpack(terms['array']); digest = hashlib.sha256(encode([DOMAIN,5,t])).digest()
        require(digest.hex() == terms['agreement_id'] and len(t) == 10, 'terms digest')
        for idx, field in ((1,'requester_signature'),(2,'provider_signature')):
            actor = next(a for a in data['actors'].values() if a['id'] == t[idx].hex())
            eddsa.new(eddsa.import_public_key(bytes.fromhex(actor['public_key'])), 'rfc8032').verify(digest, bytes.fromhex(terms[field]))
    ids = [v['id'] for v in data['vectors']]
    require(len(ids) == len(set(ids)) == 21, 'vector count/IDs')
    for v in data['vectors']:
        require(v['candidates'] == ['accounts','objects','eutxo'], 'candidate neutrality')
        require(v['client_actor'] in data['actors'], 'client attribution')
        validate_snapshot(v['initial_state'], data, v['initial_supply'])
        previous = v['initial_state']; tick = 0
        for st in v['steps']:
            event, expected = st['event'], st['expect']
            for key in ('intent',):
                if key in event:
                    require(event[key] in data['intents'], 'event intent')
            if 'observation' in event:
                require(event['observation'] in data['observations'], 'observation reference')
            if 'tick' in event:
                require(event['tick'] >= tick, 'clock reversal'); tick = event['tick']
            validate_snapshot(expected['ledger'], data, v['initial_supply'])
            result = expected['result']
            if result.startswith('reject:') or result in ('duplicate','structural_reject') or event['type'] in ('prepare','submit','crash','recover','try_new_intent'):
                require(expected['ledger'] == previous, 'nontransition changes ledger')
            if result == 'success' or result.startswith('revert:'):
                require(event['type'] == 'include', 'inclusion outcome')
                require(expected['ledger']['fee_sink'] == previous['fee_sink'] + 1, 'included fee')
                require(len(expected['ledger']['consumed']) == len(previous['consumed'])+1, 'included sequence')
                u = unpack(data['intents'][event['intent']]['unsigned'])
                actor = next(n for n,a in data['actors'].items() if a['id'] == u[2].hex())
                entry = expected['ledger']['consumed'].get(actor+':'+str(u[4]))
                require(entry == {'intent':event['intent'],'outcome':'success' if result == 'success' else 'revert'}, 'event/consumed binding')
            previous = expected['ledger']
    for obs in data['observations'].values():
        if 'state_ref' in obs:
            ref = obs['state_ref']; v = next(v for v in data['vectors'] if v['id'] == ref['vector'])
            require(0 <= ref['step'] < len(v['steps']), 'observation state reference')
    plan = load_json(directory/'stress_plan.json')
    require(len(plan['cases']) == 9, 'stress case count')
    for case in plan['cases']:
        n, c, sharing = case['delivered_actions'], case['active_clients'], case['sharing']
        allocations = [[(plan[k]//c)+(i < plan[k]%c) for i in range(c)] for k in ('principal_total','fee_total')]
        groups = ([[i] for i in range(c)] if sharing == 'disjoint' or (sharing == 'half_shared' and c == 1) else [list(range(c))] if sharing == 'shared' else [list(range(c//2))]+[[i] for i in range(c//2,c)])
        prices = [0]*c; fees = [0]*c
        for i in range(n-len(groups)):
            prices[i%c] += 1+i%3; fees[i%c] += 1
        for group in groups:
            require(sum(prices[i] for i in group) <= sum(allocations[0][i] for i in group), 'stress principal solvency')
            require(sum(fees[i] for i in group) <= sum(allocations[1][i] for i in group), 'stress fee solvency')
    require(data['run_plan']['core_vectors'] == 21 and data['run_plan']['max_runs_per_candidate'] == 91, 'run plan')
    return len(ids)


if __name__ == '__main__':
    print(f'{validate()} canonical vectors: schema, encoding, signatures, snapshots and references PASS')
