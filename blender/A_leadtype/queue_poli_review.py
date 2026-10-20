"""Wait for the shared GPU, then release it after only the requested A2 review."""
from pathlib import Path
import subprocess, sys
from render_delivery import acquire,release,BLENDER
ROOT=Path(__file__).resolve().parent
roundname=sys.argv[1] if len(sys.argv)>1 else 'round7'
token=acquire('poli_'+roundname)
try:
    with (ROOT/(roundname+'_poli.log')).open('w',encoding='utf8') as log:
        subprocess.run([BLENDER,'--background','--python-exit-code','1',str(ROOT/'leadtype_poli.blend'),
            '--python',str(ROOT/'review_saved_poli.py'),'--',roundname],stdout=log,stderr=subprocess.STDOUT,check=True)
    print('REVIEW_READY',roundname,flush=True)
finally:release(token)
