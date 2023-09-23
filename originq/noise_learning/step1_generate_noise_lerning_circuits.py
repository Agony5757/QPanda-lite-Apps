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
    inst_map = [45,46,48,52,53,54]
    coupling_map = [(45,46),(46,52),(52,53),(53,54),(54,48)]
    cz_pattern = [[],
                  [[45,46]],
                  [[46,52]],
                  [[52,53]],
                  [[53,54]],
                  [[54,48]],
                  [[45,46],[52,53]],
                  [[45,46],[53,54]],
                  [[45,46],[54,48]],
                  [[46,52],[53,54]],
                  [[46,52],[54,48]],
                  [[52,53],[54,48]],
                  [[45,46],[52,53],[54,48]]
                  ]

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