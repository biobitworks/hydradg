"""Build a tiny synthetic divergence graph for smoke testing."""
import json
from pathlib import Path

nodes = [
 {"id":"run:A","type":"Run"},
 {"id":"run:B","type":"Run"},
 {"id":"tensor:step10:loraB","type":"TensorState"},
 {"id":"eval:q1","type":"Evaluation"},
 {"id":"claim:c1","type":"Claim"},
]
edges = [
 {"src":"run:A","rel":"DEPENDS_ON","dst":"tensor:step10:loraB"},
 {"src":"run:B","rel":"FIRST_DIVERGED_AT","dst":"tensor:step10:loraB"},
 {"src":"tensor:step10:loraB","rel":"AFFECTS","dst":"eval:q1"},
 {"src":"eval:q1","rel":"AFFECTS","dst":"claim:c1"},
]
Path("synthetic_divergence_graph.json").write_text(json.dumps({"nodes":nodes,"edges":edges}, indent=2)+"\n")
print("wrote synthetic_divergence_graph.json")
