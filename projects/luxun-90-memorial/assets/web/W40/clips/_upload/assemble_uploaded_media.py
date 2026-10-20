"""One-off assembly of user-authorized local media from verified GitHub blobs."""
import base64
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

ROOT = Path.cwd()
PREFIX = 'projects/luxun-90-memorial/assets/web/'
PLAN = ROOT / (PREFIX + 'W40/clips/_upload/plan-20261020.json')
REPO = 'roanjessie236-netizen/video-scripts'

def blob_sha(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()

def fetch_chunk(part):
    req = urllib.request.Request(
        f'https://api.github.com/repos/{REPO}/git/blobs/{part["sha"]}',
        headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
                 'Accept': 'application/vnd.github.raw+json',
                 'X-GitHub-Api-Version': '2022-11-28',
                 'User-Agent': 'luxun-local-media-assembly'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                data = response.read()
                kind = response.headers.get('Content-Type', '')
            if 'json' in kind:
                body = json.loads(data)
                assert body['encoding'] == 'base64'
                data = base64.b64decode(body['content'])
            assert len(data) == part['size'], 'chunk size mismatch'
            assert blob_sha(data) == part['sha'], 'chunk hash mismatch'
            return data
        except (urllib.error.URLError, TimeoutError):
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)

def main():
    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    assert plan['repository'] == REPO and plan['branch'] == 'main'
    if not plan.get('ready'):
        print('Upload is still in progress. No media or project files changed.')
        return
    files = plan['files']
    assert len(files) == 107
    assert sum(item['binary'] for item in files) == 86
    assert len({item['path'] for item in files}) == len(files)
    for item in files:
        path = PurePosixPath(item['path'])
        assert str(path).startswith(PREFIX)
        assert not path.is_absolute() and '..' not in path.parts
        assert sum(chunk['size'] for chunk in item['chunks']) == item['size']
    with tempfile.TemporaryDirectory(prefix='luxun-media-') as folder:
        staging = Path(folder)
        for number, item in enumerate(files, 1):
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                parts = list(pool.map(fetch_chunk, item['chunks']))
            data = b''.join(parts)
            assert len(data) == item['size']
            assert blob_sha(data) == item['sha'], item['path']
            out = staging / item['path']
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
            print(f'Verified {number}/{len(files)}: {item["path"]}', flush=True)
        git('config', 'user.name', 'github-actions[bot]')
        git('config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
        for attempt in range(3):
            git('fetch', 'origin', 'main')
            # This is an isolated, disposable Actions checkout, never the user's checkout.
            git('reset', '--hard', 'origin/main')
            for item in files:
                target = ROOT / item['path']
                current = blob_sha(target.read_bytes()) if target.exists() else None
                expected = item.get('expected_base_sha')
                assert current in (expected, item['sha']), 'Concurrent edit: ' + item['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((staging / item['path']).read_bytes())
            git('add', '--', *[item['path'] for item in files])
            if not git('diff', '--cached', '--name-only'):
                print('All files already published:', git('rev-parse', 'HEAD'))
                return
            git('commit', '-m', 'Add local Lu Xun movie and complete TV scenes with Opus index')
            try:
                git('push', 'origin', 'HEAD:main')
                print('PUBLISHED_COMMIT=' + git('rev-parse', 'HEAD'), flush=True)
                return
            except subprocess.CalledProcessError:
                if attempt == 2:
                    raise

if __name__ == '__main__':
    main()
