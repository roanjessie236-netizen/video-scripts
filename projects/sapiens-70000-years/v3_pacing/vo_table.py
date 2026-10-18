import json, wave, sys
from warp import W
def ts(x):
    h,m,s=x.split(':'); s,ms=s.split(','); return int(h)*3600+int(m)*60+int(s)+int(ms)/1000
rows=[]
for b in open('/data/v2f/audio/vo_starts_v2f.srt',encoding='utf-8').read().strip().split('\n\n'):
    l=b.split('\n'); rows.append((int(l[0]),ts(l[1].split(' --> ')[0])))
SH=json.loads(sys.argv[1]) if len(sys.argv)>1 else {}
dur={i:wave.open('vo/clips/%02d.wav'%i).getnframes()/48000 for i,_ in rows}
T=[(i,W(s)+SH.get(str(i),0)) for i,s in rows]
for n,(i,u) in enumerate(T):
    old_gap=(rows[n+1][1]-rows[n][1]-dur[i]) if n+1<len(rows) else 0
    g=(T[n+1][1]-u-dur[i]) if n+1<len(T) else 0
    print('%2d old %7.2f new %7.2f dur %.2f gap %5.2f (was %5.2f)%s'%(i,rows[n][1],u,dur[i],g,old_gap,' <<' if g<1.5 else ''))
