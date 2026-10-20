"""Small wrapper: readable UTF-8 logs and reliable native exit status."""
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
args=sys.argv[1:]
name=args.pop(0)
with (ROOT/(name+".log")).open("w",encoding="utf8") as f:
    result=subprocess.run([r"D:\UE\Tools\blender.exe","--background","--python-exit-code","1",*args],stdout=f,stderr=subprocess.STDOUT)
print(f"Blender exit={result.returncode}; log={ROOT/(name+'.log')}",flush=True)
sys.exit(result.returncode)
