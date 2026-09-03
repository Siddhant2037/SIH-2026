import hashlib, mimetypes, os, shutil, subprocess, json, uuid
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[2]/"storage"
for p in ["evidence/original","evidence/derived","evidence/quarantine","thumbnails","reports"]: (ROOT/p).mkdir(parents=True,exist_ok=True)
def sha256_file(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
 return h.hexdigest()
def safe_name(name): return Path(name).name.replace(" ","_")
def ffprobe(path):
 try:
  r=subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_format","-show_streams",str(path)],capture_output=True,text=True,timeout=20)
  return json.loads(r.stdout) if r.returncode==0 else None
 except Exception:return None
def extract_frame(path,timestamp,out):
 subprocess.run(["ffmpeg","-y","-ss",str(timestamp),"-i",str(path),"-frames:v","1","-q:v","2",str(out)],capture_output=True,timeout=30)
 return out.exists()
