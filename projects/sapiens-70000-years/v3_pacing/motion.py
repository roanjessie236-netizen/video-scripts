import sys; sys.path.insert(0,'/data/v2f')
import numpy as np, core as C
pts=np.array([[0,0],[C.W,0],[0,C.H],[C.W,C.H],[C.W/2,C.H/2]],float)
for s in C.SHOTS:
    vmax=0; ts=np.arange(s['start'],s['end']-1/24,1/24)
    for t in ts:
        M0=C.cam(s,t)[0]; M1=C.cam(s,t+1/24)[0]
        # screen->source inverse: take screen pts mapped back by M0 then forward by M1
        A0=np.vstack([M0,[0,0,1]]); A1=np.vstack([M1,[0,0,1]])
        D=A1@np.linalg.inv(A0)
        q=(D[:2,:2]@pts.T).T+D[:2,2]
        v=np.abs(q-pts).max(); vmax=max(vmax,v)
    print('%-16s %6.1f-%6.1f  maxpx/frame %.2f  fx=%s'%(s['id'],s['start'],s['end'],vmax,list(s['fx'].keys())))
