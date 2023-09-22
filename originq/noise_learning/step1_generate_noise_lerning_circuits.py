import time
from generate import noise_learning_generate_circuits
import networkx as nx

def make_symmetric(Coupling_map):

    edges = Coupling_map.edges()
    edge_set = set(edges)
    for src, dest in edges:
        if (dest, src) not in edge_set:
            Coupling_map.add_edge(dest, src)
    return Coupling_map

if __name__ == '__main__':
    
    start_time = time.time()
    G = nx.DiGraph()
    # inst_map = [45,46,48,52,53,54,59,60,65,66,71]
    # inst_map = [59, 60]
    inst_map = [45,46,48,52,53,54,60]
    coupling_map = [(40,46),(45,46),(46,52),(52,53),(53,54),(54,48),(54,60),(59,60),(60,66),(66,65),(65,71)]
    # cz_pattern = [[(45,46),(52,53)],[(53,54)],[(46,52),(48,54)]]
    cz_pattern = [[(45,46),(52,53)],[(46,52),(48,54)],[(53,54)],[(54,60)],[(45,46),(52,53),(54,60)],[]]

    # inst_map = [0,1,2,3,4,5]
    # coupling_map = [(0,1),(1,2),(2,3),(3,4),(4,5)]
    # cz_pattern = [[(0,1),(2,3),(4,5)],[(1,2),(3,4)]]

    G.add_edges_from(coupling_map)
    G = make_symmetric(G)
    print(list(G.edges()))
    n_qubits = len(inst_map)
    noise_learning_generate_circuits(n_qubits,
                                     cz_pattern,
                                     G,
                                     inst_map,
                                     depth=[2,4,8,16,32],
                                     random_samples=50,
                                     multi_txt=False,
                                     select_basis=None,
                                     flip_base=False)
    end_time = time.time()
    print('time = :',end_time - start_time)