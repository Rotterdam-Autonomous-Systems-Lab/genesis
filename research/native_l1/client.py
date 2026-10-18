"""Application-level durable client, shared equally by all candidate adapters.

No ledger clone, expected outcome, private key or raw transport transaction is stored.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
from .common import packed, codec
from Crypto.Signature import eddsa


class Client:
    def __init__(self,initial,path,actors=None):
        self.path=Path(path); self.state=copy.deepcopy(initial)
        self.actors=actors or {}; self.verifications=0
        self.journal=dict(state=self.state,intents={},wrappers=[],fenced_epochs=[])
        self.flushes=0; self.journal_bytes=0
        self.persist()

    def persist(self):
        raw=packed(self.journal)
        if len(raw)>1024*1024: raise RuntimeError('journal cap')
        temporary=self.path.with_suffix('.next')
        with temporary.open('wb') as f:
            f.write(raw); f.flush(); os.fsync(f.fileno())
        os.replace(temporary,self.path)
        directory=os.open(self.path.parent,os.O_RDONLY)
        try: os.fsync(directory)
        finally: os.close(directory)
        self.flushes+=1; self.journal_bytes=max(self.journal_bytes,len(raw))

    def event(self,event,intents,observation=None,known=None,wrapper=None):
        typ=event['type']; s=self.state
        if typ=='prepare':
            if s['status']=='halted' or s['unresolved']: return 'client_blocked'
            label=event['intent']; i=intents[label]; u=codec.unpack(i['unsigned'])
            if hashlib.sha256(bytes.fromhex(i['preimage_hex'])).hexdigest()!=i['intent_id'] or codec.decode(bytes.fromhex(i['preimage_hex']))[1]!=u:
                raise RuntimeError('client intent bytes mismatch')
            if self.actors:
                actor=next(a for a in self.actors.values() if a['id']==u[2].hex())
                h=hashlib.sha256(bytes.fromhex(i['preimage_hex'])).digest()
                eddsa.new(eddsa.import_public_key(bytes.fromhex(actor['public_key'])),'rfc8032').verify(h,bytes.fromhex(i['signature']))
                self.verifications+=1
            s['queries']=0; s['submissions']=0
            amount=u[8][-2] if u[7]==1 else u[8][2][7] if u[7]==5 else u[8][4]+u[8][5] if u[7]==2 else 0
            s.update(status='prepared',principal_reserved=amount,fee_reserved=u[6],unresolved=[label])
            self.journal['intents'][label]=dict(id=i['intent_id'],epoch=u[3],sequence=u[4],network=u[1].hex(),preimage_hex=i['preimage_hex'])
            self.persist(); return 'prepared'
        if typ in ('submit','attempt'):
            if s['status']=='halted' or not s['unresolved']: return 'client_blocked'
            if s['submissions']>=3: raise RuntimeError('submission cap')
            if not wrapper or wrapper.get('intent_id')!=self.journal['intents'][s['unresolved'][0]]['id']:
                raise RuntimeError('client wrapper intent mismatch')
            # Durable identity before broadcast. Do not publish raw transport wrappers.
            self.journal['wrappers'].append(dict(id=hashlib.sha256(packed(wrapper)).hexdigest(),epoch=len(self.journal['fenced_epochs'])))
            s['submissions']+=1; s['status']='unknown'; self.persist()
            return 'structural_reject' if typ=='attempt' else 'unknown'
        if typ=='crash':
            # Discard volatile state and reload the last fsynced journal.
            self.journal=None; self.state=None
            self.journal=json.loads(self.path.read_text()); self.state=self.journal['state']; s=self.state
            s['status']='crashed'; self.persist(); return 'crashed'
        if typ=='include':
            if s['unresolved'] and not event.get('reply_lost'):
                s['status']='included'; self.persist()
            return None
        if typ=='rollback':
            if s['unresolved']: s['status']='orphaned'; self.persist()
            return 'orphaned'
        if typ=='try_new_intent':
            if s['unresolved'] or s['status']=='halted': return 'client_blocked'
            raise RuntimeError('unexpected new-intent creation')
        if typ=='recover':
            if s['queries']>=8: raise RuntimeError('query cap')
            s['queries']+=1
            obs=observation or {}; kind=obs.get('kind')
            if kind=='conflicting_final': result='halted:assumption_breach'
            elif s['status']=='halted' and kind!='unavailable': result='halted:contradiction'
            elif kind=='unavailable': result='halted:unknown'
            elif kind!='oracle': result='halted:contradiction'
            elif obs.get('outcome')=='not_admitted':
                # Trust belongs to the scheduler, not agreement among RPC replies.
                if not obs.get('fenced') or known or not s['unresolved']: result='halted:contradiction'
                else:
                    self.journal['fenced_epochs'].append(len(self.journal['fenced_epochs']))
                    s['status']='retry_ready'; self.persist(); return 'same_intent_retry_allowed'
            elif obs.get('final') and obs.get('outcome') in ('success','revert') and known==obs.get('outcome'):
                for label in s['unresolved']:
                    entry=self.journal['intents'][label]
                    self.journal['intents'][label]=dict(id=entry['id'],final_outcome=known)
                self.journal['wrappers']=[]
                s.update(status='final',principal_reserved=0,fee_reserved=0,unresolved=[])
                self.persist(); return 'reconciled'
            else: result='halted:contradiction'
            s['status']='halted'; self.persist(); return result
        raise RuntimeError('unknown client event')
