import subprocess, numpy as np
SRC = '/data/film/src.mp4'
W, H = 2560, 1440
def grab(k, n=1):
    """exact user frames k..k+n-1 (30 fps) as BGR uint8"""
    t = max(0.0, k / 30.0 - 0.0005)
    cmd = ['ffmpeg', '-v', 'error', '-ss', '%.4f' % t, '-i', SRC, '-frames:v', str(n), '-f', 'rawvideo',
           '-pix_fmt', 'bgr24', '-']
    b = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(b, np.uint8).reshape(-1, H, W, 3)
