import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from e2e_lib import jsd_bits, cloud_drift, exact_agreement, cohen_kappa_if_informative

def test_jsd_identity():
    assert abs(jsd_bits([1,2,3],[1,2,3])) < 1e-12
    assert abs(cloud_drift([1,2,3],[1,2,3])) < 1e-10

def test_jsd_bounded():
    x=jsd_bits([1,0],[0,1])
    assert abs(x-1.0) < 1e-12
    assert abs(cloud_drift([1,0],[0,1])-100.0)<1e-10

def test_kappa_single_class_is_not_informative():
    a=["DEPTH_RECOVERY"]*3
    b=["DEPTH_RECOVERY"]*3
    assert exact_agreement(a,b)==1.0
    assert cohen_kappa_if_informative(a,b) is None

def test_kappa_with_variation():
    a=["A","A","B","B"]
    b=["A","B","B","B"]
    k=cohen_kappa_if_informative(a,b)
    assert k is not None
