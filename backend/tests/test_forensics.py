import sys,tempfile,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.services import sha256_file,safe_name
def test_sha256():
 with tempfile.NamedTemporaryFile(delete=False) as f:f.write(b"trace-x")
 p=Path(f.name);assert sha256_file(p)==hashlib.sha256(b"trace-x").hexdigest();p.unlink()
def test_safe_name(): assert safe_name("../../evil.bin")=="evil.bin"
