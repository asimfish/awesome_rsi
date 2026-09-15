"""Exhaustively verify 8-bit combinational adders. Stdlib only.
Gate count / depth use a unit-delay Boolean DAG, NOT synthesized PPA.
Run from anywhere: python3 verify_adders.py
"""
from pathlib import Path
import json, hashlib, datetime

class Circuit:
    def __init__(self):
        self.nodes=[('INPUT',[],f'a{i}') for i in range(8)]+[('INPUT',[],f'b{i}') for i in range(8)]+[('INPUT',[],'cin')]
        self.depth=[0]*17
    def gate(self,op,*args):
        self.nodes.append((op,list(args),''));self.depth.append(1+max(self.depth[x] for x in args));return len(self.nodes)-1
    def evaluate(self,a,b,ci):
        v=[(a>>i)&1 for i in range(8)]+[(b>>i)&1 for i in range(8)]+[ci]
        for op,args,_ in self.nodes[17:]:
            x,y=(v[t] for t in args)
            v.append(x^y if op=='XOR' else x&y if op=='AND' else x|y)
        return sum(v[x]<<i for i,x in enumerate(self.outputs))

def build(kind):
    c=Circuit();p=[c.gate('XOR',i,i+8) for i in range(8)];g=[c.gate('AND',i,i+8) for i in range(8)]
    if kind=='ripple':
        carries=[16]
        for i in range(8):carries.append(c.gate('OR',g[i],c.gate('AND',p[i],carries[-1])))
    else:
        pg,gg=p[:],g[:]
        for step in [1,2,4]:
            oldp,oldg=pg[:],gg[:]
            for i in range(step,8):
                gg[i]=c.gate('OR',oldg[i],c.gate('AND',oldp[i],oldg[i-step]))
                pg[i]=c.gate('AND',oldp[i],oldp[i-step])
        carries=[16]+[c.gate('OR',gg[i],c.gate('AND',pg[i],16)) for i in range(8)]
    c.outputs=[c.gate('XOR',p[i],carries[i]) for i in range(8)]+[carries[8]]
    return c

def main():
    results=[]
    for kind in ['ripple','prefix','broken']:
        c=build('ripple' if kind=='ripple' else 'prefix');fails=0;first=None
        for a in range(256):
            for b in range(256):
                for ci in [0,1]:
                    actual=c.evaluate(a,b,0 if kind=='broken' else ci);expected=a+b+ci
                    if actual!=expected:
                        fails+=1
                        if first is None:first=dict(a=a,b=b,cin=ci,expected=expected,actual=actual)
        results.append(dict(id=kind,inputs=131072,passed=131072-fails,failed=fails,first_counterexample=first,
                            gates=len(c.nodes)-17,depth=max(c.depth[i] for i in c.outputs),status='PASS' if not fails else 'FAIL'))
    assert results[0]['failed']==results[1]['failed']==0
    assert results[2]['failed']==65536
    assert results[1]['depth']<results[0]['depth']
    out=dict(kind='local_exhaustive_boolean_verification',generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        scope='8-bit unsigned a+b+cin; all 131072 inputs; unit-delay AND/OR/XOR network; no RTL synthesis, SEC, PDK, or LLM search',
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),results=results)
    p=Path(__file__).resolve().parents[1]/'data/local-experiment.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
