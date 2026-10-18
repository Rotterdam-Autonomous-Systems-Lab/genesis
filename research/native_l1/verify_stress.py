"""Public artifact verification, separate from candidates and generator mutations."""
import hashlib
from Crypto.Signature import eddsa
from .common import codec,DOMAIN
from .checks import require


def verify(data,corpus,plan):
    require(len(data['cases'])==9,'stress count')
    for case,spec in zip(data['cases'],plan['cases']):
        m=case['manifest'];require(case['id']==spec['id'],'stress order')
        require(len(case['operations'])==spec['delivered_actions'],'stress action count')
        require(m['network_id']==corpus['network_id'] and m['service_id']==corpus['service_id'],'stress domains')
        for label,intent in m['intents'].items():
            raw=bytes.fromhex(intent['preimage_hex']); u=codec.unpack(intent['unsigned'])
            require(codec.decode(raw)==[DOMAIN,u],'stress canonical bytes')
            h=hashlib.sha256(raw).digest();require(h.hex()==intent['intent_id'],'stress intent digest')
            actor=next(a for a in m['actors'].values() if a['id']==u[2].hex())
            eddsa.new(eddsa.import_public_key(bytes.fromhex(actor['public_key'])),'rfc8032').verify(h,bytes.fromhex(intent['signature']))
            if u[7]==5:
                t=u[8][2];d=hashlib.sha256(codec.encode([DOMAIN,5,t])).digest()
                for index,sig in ((1,u[8][3]),(2,u[8][4])):
                    actor=next(a for a in m['actors'].values() if a['id']==t[index].hex())
                    eddsa.new(eddsa.import_public_key(bytes.fromhex(actor['public_key'])),'rfc8032').verify(d,sig)
