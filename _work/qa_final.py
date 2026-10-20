import sys, runpy, glob, subprocess, imageio_ffmpeg
f = [p for p in glob.glob('video/out/*.mp4') if '字幕版' in p and '无' not in p][0]
sys.argv = ['qa', f, '2']
runpy.run_path('tools/qa_video.py', run_name='__main__')
FF = imageio_ffmpeg.get_ffmpeg_exe()
for t in [20, 44, 47, 60, 125, 132, 470, 500, 513, 530, 545, 558]:
    subprocess.run([FF, '-loglevel', 'error', '-y', '-ss', str(t), '-i', f, '-frames:v', '1', '-vf', 'scale=960:-1', f'video/out/stills/final_{t:03d}.jpg'])
