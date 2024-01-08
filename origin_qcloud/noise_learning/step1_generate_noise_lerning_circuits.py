import time
from generate import noise_learning_generate_circuits
import networkx as nx
from qpandalite.task.originq_dummy import available_qubits, available_topology

def make_symmetric(Coupling_map):

    edges = Coupling_map.edges()
    edge_set = set(edges)
    for src, dest in edges:
        if (dest, src) not in edge_set:
            Coupling_map.add_edge(dest, src)
    return Coupling_map

inst_map = available_qubits
coupling_map = available_topology
pattern1 = [[1,2],[3,4],[8,9],[10,11],[13,14],[15,16],[17,18],[25,26],[27,28],[29,30],[32,33],[34,35],[37,38],[39,40],[49,50],[61,62],[68,69]]
pattern2 = [[2,3],[7,8],[11,12],[14,15],[19,20],[26,27],[31,32],[33,34],[35,36],[38,39],[45,46],[47,48],[50,51],[57,58],[62,63],[67,68],[71,72]]
pattern3 = [[1,7],[3,9],[8,14], [10,16],[12,18],[13,19],[17,23],[20,26],[25,31],[27,33],[29,35],[34,40],[36,42],[37,43],[39,45],[51,57],[61,67],[63,69]]
pattern4 = [[2,8],[4,10],[7,13],[9,15],[11,17],[14,20],[19,25],[23,29],[26,32],[28,34],[30,36],[31,37],[33,39],[40,46],[42,48],[43,49],[45,51],[47,53],[50,56],[55,61],[57,63],[62,68],[66,72]]                     
tmp_cz_patterns = [pattern1, pattern2, pattern3, pattern4]
# tmp_cz_patterns = [pattern1]
cz_patterns = []
for tmp_pattern in tmp_cz_patterns:
    pattern = [[i-1,j-1] for i, j in tmp_pattern]
    cz_patterns.append(pattern)

if __name__ == '__main__':
    
    start_time = time.time()
    G = nx.DiGraph()

    G.add_edges_from(coupling_map)
    G = make_symmetric(G)
    print(list(G.edges()))
    n_qubits = len(inst_map)
    noise_learning_generate_circuits(n_qubits,
                                     cz_patterns,
                                     G,
                                     inst_map,
                                     depth=[2,4,8,16,32,64],
                                     random_samples=100,
                                     multi_txt=True,
                                     select_basis=None,
                                     flip_base=False)
    end_time = time.time()
    print('time = :',end_time - start_time)