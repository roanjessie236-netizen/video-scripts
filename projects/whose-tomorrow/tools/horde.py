"""AI Horde client (anonymous key unless HORDE_KEY). usage: horde.py OUT.png 'prompt' [model] [w] [h] [seed] [steps] [cfg] [sampler]"""
import json, os, sys, time, urllib.request, base64
API = 'https://aihorde.net/api/v2'
KEY = os.environ.get('HORDE_KEY', '0000000000')
def req(path, data=None, method=None):
    r = urllib.request.Request(API + path, data=json.dumps(data).encode() if data is not None else None, method=method,
                               headers={'apikey': KEY, 'Content-Type': 'application/json', 'Client-Agent': 'wt-film:1.0:none', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) wt-film/1.0'})
    return json.load(urllib.request.urlopen(r, timeout=60))
def gen(out, prompt, model='Z-Image-Turbo', w=1344, h=768, seed=7, steps=9, cfg=1.0, sampler='k_euler', neg=''):
    p = dict(prompt=prompt + ('###' + neg if neg else ''), params=dict(width=w, height=h, steps=steps, cfg_scale=cfg,
             sampler_name=sampler, seed=str(seed), n=1, karras=False), models=[model], r2=True, nsfw=False, censor_nsfw=False,
             trusted_workers=False, slow_workers=True)
    j = req('/generate/async', p); i = j['id']; t = time.time()
    while True:
        time.sleep(4); s = req('/generate/check/' + i)
        if s.get('done'): break
        if s.get('faulted') or not s.get('is_possible', True): raise RuntimeError('faulted/impossible %s' % s)
        if time.time() - t > 900: raise RuntimeError('timeout')
    r = req('/generate/status/' + i)['generations'][0]
    img = r['img']
    data = urllib.request.urlopen(img, timeout=120).read() if img.startswith('http') else base64.b64decode(img)
    open(out, 'wb').write(data)
    return time.time() - t, r.get('worker_name'), j.get('kudos')
if __name__ == '__main__':
    a = sys.argv[1:]
    print(gen(a[0], a[1], *(a[2:3] or ['Z-Image-Turbo']), *[int(x) for x in a[3:6]]))
