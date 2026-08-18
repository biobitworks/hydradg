from __future__ import annotations
from pathlib import Path
import hashlib,json,datetime,os,fcntl

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")

def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()

def sha_file(p):
    return sha_bytes(Path(p).read_bytes())

def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def fco_id(kind,payload):
    body={"type":kind,"payload":payload}
    return "fco:"+sha_bytes(canon(body))

def fcg_id(src,rel,dst,payload):
    body={"src":src,"rel":rel,"dst":dst,"payload":payload or {}}
    return "fcg:"+sha_bytes(canon(body))

def append_unique(path, rec):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    idv=rec["id"]
    with path.open("a+",encoding="utf-8") as f:
        fcntl.flock(f.fileno(),fcntl.LOCK_EX)
        f.seek(0)
        for line in f:
            try:
                if json.loads(line).get("id")==idv:
                    fcntl.flock(f.fileno(),fcntl.LOCK_UN)
                    return False
            except Exception:
                pass
        f.seek(0,2)
        f.write(json.dumps(rec,sort_keys=True,ensure_ascii=False)+"\n")
        f.flush(); os.fsync(f.fileno())
        fcntl.flock(f.fileno(),fcntl.LOCK_UN)
    return True

def add_node(graph_dir,kind,payload):
    oid=fco_id(kind,payload)
    rec={"id":oid,"object_sha256":oid.split(":",1)[1],"type":kind,"payload":payload}
    append_unique(Path(graph_dir)/"nodes.jsonl",rec)
    return oid

def add_edge(graph_dir,src,rel,dst,payload=None):
    payload=payload or {}
    eid=fcg_id(src,rel,dst,payload)
    rec={"id":eid,"src":src,"rel":rel,"dst":dst,"payload":payload}
    append_unique(Path(graph_dir)/"edges.jsonl",rec)
    return eid
