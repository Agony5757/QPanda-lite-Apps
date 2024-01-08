import networkx as nx
from itertools import cycle, permutations, product


def generate_subgraph(G,inst_map):
    
    subgraph_nodes = inst_map
    subgraph = G.subgraph(subgraph_nodes)

    return subgraph


def generate_meas_bases(subGraph,inst_map):

    NUM_BASES = 9
    n = len(inst_map)
    bases = [['I']*n for i in range(NUM_BASES)]
    mapping_inst_map_to_logic = {}
    for ind,node in enumerate(inst_map):
        mapping_inst_map_to_logic[node] = ind
    for index,vertex in enumerate(inst_map):
        orderings = {"XXXYYYZZZ":"XYZXYZXYZ",
                            "XXXYYZZZY":"XYZXYZXYZ",
                            "XXYYYZZZX":"XYZXYZXYZ",
                            "XXZYYZXYZ":"XYZXZYZYX",
                            "XYZXYZXYZ":"XYZZXYYZX"}
        
        children = subGraph.neighbors(vertex)
        predecessors = [c for c in children if c < vertex]

        if not predecessors:
            cycp = cycle("XYZ")
            for i,_ in enumerate(bases):
                bases[i][index] = next(cycp)

        elif len(predecessors) == 1:
            pred, = predecessors
            _,bases = list(zip(*sorted(zip([p[mapping_inst_map_to_logic[pred]] for p in bases], bases))))
            cycp = cycle("XYZ")
            for i,_ in enumerate(bases):
                bases[i][index] = next(cycp)
        elif len(predecessors) == 2:
            pred0,pred1 = predecessors
            
            _,bases = list(zip(*sorted(zip([p[mapping_inst_map_to_logic[pred0]] for p in bases], bases))))
            substr = [p[mapping_inst_map_to_logic[pred1]] for p in bases]
            reordering = ""
            for perm in permutations("XYZ"):
                substr = "".join(["XYZ"[perm.index(p)] for p in substr])
                if substr in orderings:
                    current = orderings[substr] 
                    for i,p in enumerate(current):
                        bases[i][index] = p
                    break
        else:
            raise Exception("Three or more predecessors encountered")

    # bases = ["".join(b)[::-1] for b in bases]
    bases = ["".join(b) for b in bases]
    
    return [string for string in bases]


def generate_model_terms(subGraph,inst_map):
    n = len(inst_map)
    model_terms = set()
    identity = ["I"]*n 
    mapping_inst_map_to_logic = {}
    for ind,node in enumerate(inst_map):
        mapping_inst_map_to_logic[node] = ind
    for q1,q2 in subGraph.edges():
        k=1
        for p1, p2 in product("IXYZ", repeat=2):
            pauli = identity.copy()
            pauli[mapping_inst_map_to_logic[q1]] = p1
            pauli[mapping_inst_map_to_logic[q2]] = p2
            # (NO) reverse to meet the measurement sequence
            # model_terms.add("".join(reversed(pauli)))
            model_terms.add("".join(pauli))
    for q in subGraph.nodes():
        for p in "IXYZ":
            pauli = identity.copy()
            pauli[mapping_inst_map_to_logic[q]] = p
            
            # (NO) reverse to meet the measurement sequence
            # model_terms.add("".join(reversed(pauli)))
            model_terms.add("".join(pauli))

    model_terms.remove("".join(identity))
    
    return [p for p in model_terms]


