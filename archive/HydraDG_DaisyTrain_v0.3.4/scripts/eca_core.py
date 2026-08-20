import hashlib, json, random

RULES=(30,90,110,184)
PAIR_RULE={30:110,90:30,110:184,184:90}
WIDTH=129
STEPS=96
TAMPER_T=30
RULE_DRIFT_T=40
REPAIR_T=31
MASTER_SEED=20260817

def rule_bit(rule,left,center,right):
    idx=(left<<2)|(center<<1)|right
    return (rule >> idx) & 1

def evolve(state,rule):
    n=len(state)
    return [rule_bit(rule,state[(i-1)%n],state[i],state[(i+1)%n]) for i in range(n)]

def state_hash(state):
    b=bytes(state)
    return hashlib.sha256(b).hexdigest()

def make_seed(rule,seed_index):
    r=random.Random((MASTER_SEED<<16) ^ (rule<<8) ^ seed_index)
    s=[0]*WIDTH
    # sparse deterministic seed plus center anchor
    for i in range(WIDTH):
        if r.random()<0.08:
            s[i]=1
    s[WIDTH//2]=1
    return s

def baseline(rule,seed_index):
    s=make_seed(rule,seed_index)
    states=[s[:]]
    for _ in range(STEPS-1):
        s=evolve(s,rule); states.append(s[:])
    return states

def run_one(rule,seed_index,condition):
    base=baseline(rule,seed_index)
    s=base[0][:]
    states=[s[:]]
    perturbation=None
    for t in range(1,STEPS):
        active_rule=rule
        if condition=="rule_drift" and t>=RULE_DRIFT_T:
            active_rule=PAIR_RULE[rule]
            if t==RULE_DRIFT_T:
                perturbation={"kind":"rule_drift","step":t,"from_rule":rule,"to_rule":active_rule}
        s=evolve(s,active_rule)
        if condition in ("cell_tamper","oracle_repair") and t==TAMPER_T:
            pos=WIDTH//2
            s[pos]^=1
            perturbation={"kind":"cell_tamper","step":t,"cell":pos}
        if condition=="oracle_repair" and t==REPAIR_T:
            # oracle repair sets the complete state back to the reference state at this time.
            s=base[t][:]
        states.append(s[:])
    hamming=[sum(a!=b for a,b in zip(states[t],base[t])) for t in range(STEPS)]
    first=next((t for t,d in enumerate(hamming) if d),None)
    recovery=next((t for t in range((first or 0)+1,STEPS)
                   if hamming[t]==0 and all(x==0 for x in hamming[t:])),None) if first is not None else None
    return {
      "rule":rule,"seed_index":seed_index,"condition":condition,
      "master_seed":MASTER_SEED,"width":WIDTH,"steps":STEPS,
      "perturbation":perturbation,
      "first_divergence_step":first,
      "expected_first_divergence_step":(
          TAMPER_T if condition in ("cell_tamper","oracle_repair")
          else RULE_DRIFT_T if condition=="rule_drift" else None
      ),
      "hamming_by_step":hamming,
      "state_hashes":[state_hash(x) for x in states],
      "baseline_state_hashes":[state_hash(x) for x in base],
      "state_exact_recovery_step":recovery,
      "recovery_class":(
        "NOT_APPLICABLE" if condition=="baseline"
        else "STATE_EXACT" if recovery is not None
        else "NO_EXACT_RECOVERY"
      )
    }

def generate(full=True):
    seed_indices=range(5 if full else 1)
    rules=RULES if full else (30,90)
    conditions=("baseline","cell_tamper","rule_drift","oracle_repair")
    rows=[run_one(r,s,c) for r in rules for s in seed_indices for c in conditions]
    pert=[x for x in rows if x["condition"]!="baseline"]
    repair=[x for x in rows if x["condition"]=="oracle_repair"]
    summary={
      "total_trajectories":len(rows),
      "perturbed_trajectories":len(pert),
      "first_divergence_exact":sum(
        x["first_divergence_step"]==x["expected_first_divergence_step"] for x in pert
      ),
      "oracle_repair_trajectories":len(repair),
      "state_exact_recovery":sum(x["recovery_class"]=="STATE_EXACT" for x in repair)
    }
    obj={
      "schema":"hydradg.eca_extension.v0.3.1",
      "experiment_id":"ECA-EXT80" if full else "ECA-EXT-QUICK",
      "status":"RECOMPUTED_RESULT",
      "design":{
        "rules":list(rules),"seed_indices":list(seed_indices),
        "conditions":list(conditions),"master_seed":MASTER_SEED,
        "width":WIDTH,"steps":STEPS,"tamper_step":TAMPER_T,
        "rule_drift_step":RULE_DRIFT_T,"oracle_repair_step":REPAIR_T
      },
      "summary":summary,
      "trajectories":rows,
      "claim_ceiling":"BOUNDED_DETERMINISTIC_CONFORMANCE"
    }
    canonical=json.dumps(obj,sort_keys=True,separators=(",",":")).encode()
    obj["result_body_sha256"]=hashlib.sha256(canonical).hexdigest()
    return obj
