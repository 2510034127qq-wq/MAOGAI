"""Exclusive, recoverable GPU queue. No writes outside task, shot dirs and lock."""
from pathlib import Path
from datetime import datetime, timezone
import json
import os
import subprocess
import time
import uuid
import argparse

ROOT=Path(__file__).resolve().parent
RENDERS=ROOT.parents[1]/"assets"/"renders"
LOCK=RENDERS/".gpu.lock"
BLENDER=r"D:\UE\Tools\blender.exe"


def acquire(shot):
    token=str(uuid.uuid4())
    while True:
        try:
            with LOCK.open("x",encoding="utf8") as f:
                json.dump({"task":"A_leadtype","shot":shot,"owner":token,"pid":os.getpid(),
                           "started_utc":datetime.now(timezone.utc).isoformat()},f)
            print("GPU_LOCK_ACQUIRED",shot,token,flush=True)
            return token
        except FileExistsError:
            try:
                age=time.time()-LOCK.stat().st_mtime
                if age>90*60:
                    print("STALE_LOCK_REMOVED",LOCK.read_text(encoding="utf8"),flush=True)
                    LOCK.unlink()
                    continue
                print("GPU_WAIT",LOCK.read_text(encoding="utf8"),flush=True)
            except FileNotFoundError:
                continue
            time.sleep(60)


def release(token):
    try:
        if json.loads(LOCK.read_text(encoding="utf8")).get("owner")==token:
            LOCK.unlink()
    except FileNotFoundError:pass


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--shot',choices=['title','poli','both'],default='both')
    args=parser.parse_args()
    for shot in ("title","poli"):
        if args.shot not in ('both',shot):continue
        token=acquire(shot)
        proc=None
        try:
            with (ROOT/f"production_{shot}.log").open("w",encoding="utf8") as log:
                proc=subprocess.Popen([BLENDER,"--background","--python-exit-code","1",
                    str(ROOT/f"leadtype_{shot}.blend"),"--python",str(ROOT/"render_worker.py"),"--",shot,token],
                    stdout=log,stderr=subprocess.STDOUT)
                code=proc.wait()
            if code:raise RuntimeError(f"Render {shot} failed, exit {code}")
            print("RENDER_FINISHED",shot,flush=True)
        finally:
            if proc and proc.poll() is None:
                proc.terminate();proc.wait()
            release(token)


if __name__=="__main__":main()
