#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,os,re,sys

roots=[
    Path.cwd()/".agents/skills",
    Path.home()/".gemini/config/skills",
    Path.home()/".gemini/antigravity-cli/skills",
    Path.home()/".gemini/skills",
]
hits=[]
all_skills=[]
for root in roots:
    if not root.exists():
        continue
    for p in sorted(root.glob("*/SKILL.md")):
        try:
            text=p.read_text(errors="replace")
        except Exception:
            continue
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        m=re.search(r"(?mi)^name:\s*(.+?)\s*$",text)
        d=re.search(r"(?mi)^description:\s*(.+?)\s*$",text)
        item={
            "path":str(p),
            "sha256":h,
            "name":m.group(1).strip() if m else p.parent.name,
            "description":d.group(1).strip() if d else None,
        }
        all_skills.append(item)
        blob=(item["name"]+" "+str(item["description"])+" "+text[:5000]).lower()
        if ("fco" in blob or "fractal custody" in blob or
            "fractal context object" in blob or "fcg" in blob):
            hits.append(item)

out={
  "schema":"hydradg.fco_skill_audit.v1",
  "status":"FCO_SKILL_FOUND" if hits else "FCO_SKILL_NOT_FOUND",
  "searched_roots":[str(x) for x in roots],
  "fco_candidates":hits,
  "loaded_skill_count_not_proven_by_filesystem":len(all_skills),
  "note":"Filesystem discovery proves presence only. Use Antigravity /skills to prove the skill is loaded in the active Project."
}
print(json.dumps(out,indent=2,sort_keys=True))
sys.exit(0 if hits else 2)
