import pyqpanda as pq
import numpy as np
import random
from subgraph import generate_meas_bases,generate_subgraph,generate_model_terms
import networkx as nx
import time
import json
from pathlib import Path
import os
TWIRL_GATES = {
    "cx": (
        (("I", "I"), ("I", "I")),
        (("I", "X"), ("I", "X")),
        (("I", "Y"), ("Z", "Y")),
        (("I", "Z"), ("Z", "Z")),
        (("X", "I"), ("X", "X")),
        (("X", "X"), ("X", "I")),
        (("X", "Y"), ("Y", "Z")),
        (("X", "Z"), ("Y", "Y")),
        (("Y", "I"), ("Y", "X")),
        (("Y", "X"), ("Y", "I")),
        (("Y", "Y"), ("X", "Z")),
        (("Y", "Z"), ("X", "Y")),
        (("Z", "I"), ("Z", "I")),
        (("Z", "X"), ("Z", "X")),
        (("Z", "Y"), ("I", "Y")),
        (("Z", "Z"), ("I", "Z")),
    ),
    "cz": (
        (("I", "I"), ("I", "I")),
        (("I", "X"), ("Z", "X")),
        (("I", "Y"), ("Z", "Y")),
        (("I", "Z"), ("I", "Z")),
        (("X", "I"), ("X", "Z")),
        (("X", "X"), ("Y", "Y")),
        (("X", "Y"), ("Y", "X")),
        (("X", "Z"), ("X", "I")),
        (("Y", "I"), ("Y", "Z")),
        (("Y", "X"), ("X", "Y")),
        (("Y", "Y"), ("X", "X")),
        (("Y", "Z"), ("Y", "I")),
        (("Z", "I"), ("Z", "I")),
        (("Z", "X"), ("I", "X")),
        (("Z", "Y"), ("I", "Y")),
        (("Z", "Z"), ("Z", "Z")),
    ),
}

strs = 'I X Y Z'.split()

def generate_twirl(rand1,rand2):
    pair = (rand1, rand2)
    for x,y in TWIRL_GATES['cz']:
        if x == pair:
            return y
    raise NotImplementedError
        

def random_pauli(left = 0,right = 3):
    return strs[random.randint(left, right)]

def random_rostring(n_qubits):
    ro_string =''
    for i in range(n_qubits):
        ro_string += str(random.randint(0, 1))
    return  ro_string

def generate_pauli_twirls():
    l1 = random_pauli()
    l2 = random_pauli()
    r1, r2 = generate_twirl(l1, l2)
    return l1,l2,r1,r2

def readout_twirl(qubits_list,n_qubits):
    originir = ''
    ro_string = random_rostring(n_qubits)
    for ind,char in enumerate(ro_string):
        if char == '1': 
           originir +=(
               f'X q[{qubits_list[ind]}]\n'
           )
    for ind,qubit in enumerate(qubits_list):
        originir +=(
            f'MEASURE q[{qubit}],c[{ind}]\n'
        )           
    return originir,ro_string
        
def bairrer_all(qubit_list):
    originir = ''
    for ind,qubit in enumerate(qubit_list):
        if ind ==0:
            originir += (f'BARRIER q[{qubit}],')
            continue
        elif ind == len(qubit_list) -1:
            originir += (f'q[{qubit}]\n')
        else:
            originir += (f'q[{qubit}],')
    return originir

def create_no_optimize_pauli(pauli, qubit):
    if pauli == 'X':
        return f'Rphi q[{qubit}], (1.5707963, 0)' + '\n' + f'Rphi q[{qubit}], (1.5707963, 0)'
    if pauli == 'Y':
        return f'Rphi q[{qubit}], (1.5707963, 1.5707963)' + '\n' + f'Rphi q[{qubit}], (1.5707963, 1.5707963)'
    if pauli == 'Z':
        return create_no_optimize_pauli('X', qubit) + '\n' + create_no_optimize_pauli('Y', qubit)
    if pauli == 'I':
        return ''
    
def generate_pauli_twirl_circuit(qubit_set,cz_pattern,repeats = 40):
    
    repeats_inst = ''
    idle_qubit_set = qubit_set.copy()
    qubit_list = list(qubit_set)
    
    for pair in cz_pattern:
        if pair[0] in idle_qubit_set:
            idle_qubit_set.remove(pair[0])
        if pair[1] in idle_qubit_set:
            idle_qubit_set.remove(pair[1])    
    for i in range(repeats):
        pauli_list = []
        clifford_conj_list = []
        
        for qubit in idle_qubit_set:
            pauli = random_pauli(1,3)
            pauli_list.append(pauli)
            repeats_inst += (
                f'{pauli} q[{qubit}]\n')    
                                                       
        for pair in cz_pattern:
            l1,l2,r1,r2 = generate_pauli_twirls()
            clifford_conj_list.append((r1,r2))
            
            repeats_inst += (f'{l1} q[{pair[0]}]\n')
            repeats_inst += (f'{l2} q[{pair[1]}]\n')
                
        repeats_inst += bairrer_all(qubit_list)
        
        for pair in cz_pattern:  
            repeats_inst += (f'CZ q[{pair[0]}],q[{pair[1]}]\n')
            
        repeats_inst += bairrer_all(qubit_list)
        
        for ind,qubit in enumerate(idle_qubit_set):
            pauli = pauli_list[ind]
            repeats_inst += (
            f'{pauli} q[{qubit}]\n')  
                                            
        for clifford_pair,pair in zip(clifford_conj_list,cz_pattern):     
            repeats_inst += (
                f'{clifford_pair[0]} q[{pair[0]}]\n')
            repeats_inst += (
                f'{clifford_pair[1]} q[{pair[1]}]\n')
        repeats_inst += bairrer_all(qubit_list)

    return repeats_inst

def change_prep_base(qubit_list,meas_bases,flip_base = False):
    originir = ''
    for ind,char in enumerate(meas_bases[::-1]):
        if flip_base:
            originir += f'X q[{qubit_list[ind]}]\n'

        if char =='X':
            originir +=( 
                f'H q[{qubit_list[ind]}]\n'
            )
        elif char == 'Y':
            originir +=( 
                f'RX q[{qubit_list[ind]}],({-np.pi/2})\n'
            )
            
    return originir

def change_meas_base(qubit_list,meas_bases,flip_base = False):
    originir = ''
    for ind,char in enumerate(meas_bases[::-1]):
        if char =='X':
            originir +=( 
                f'H q[{qubit_list[ind]}]\n'
            )
        elif char == 'Y':
            originir +=( 
                f'RX q[{qubit_list[ind]}],({np.pi/2})\n'
            )
        if flip_base:
            originir += f'X q[{qubit_list[ind]}]\n'
    return originir

def noise_learning_generate_circuits(n_qubits,
                                     cz_pattern,
                                     coupling_map,
                                     inst_map,
                                     depth = [2,4,8],
                                     random_samples = 40,
                                     multi_txt = False,
                                     select_basis = None,
                                     flip_base=False):
    """Error mitigation noise leaning circuits generate code

    Args:
        n_qubits (int): number of qubits
        cz_pattern (list(tuple)): Parallel CZ pattern
        coupling_map (networx graph): Chip topology (directed acyclic graph)
        inst_map (layout map): Mapping qubit list
        depth (list, optional): noise learning depth Defaults to [2,4,8].
        random_samples (int, optional): Random samples per depth. Defaults to 40.
        multi_txt (bool, optional): OriginIR txt save in single txt or multi txts. 
    """

    max_qubit = 1 + max(inst_map)

    phyical_qubits_to_logiacl_qubits = {}
    for ind,qubit in enumerate(inst_map):
        phyical_qubits_to_logiacl_qubits[qubit] = ind

    subgraph = generate_subgraph(coupling_map,inst_map)
    if not select_basis:
        meas_bases = generate_meas_bases(subgraph,inst_map)
    else:
        meas_bases = select_basis
    model_terms = generate_model_terms(subgraph,inst_map)
    
    originir = ''
    circuit_data = {}
    circuit_data['mapping_qubits'] = phyical_qubits_to_logiacl_qubits
    circuit_data['model_terms'] = model_terms
    circuit_data['cz_patterns'] = cz_pattern
    output_path = Path.cwd() / 'output_circuits'
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        
    for index,pattern in enumerate(cz_pattern):
        print(pattern)
        count = 0 
        for base in meas_bases:
            for layer in depth:
                for sample in range(random_samples):
                    if multi_txt:
                        originir = ''

                    originir += (
                        f'QINIT {max_qubit}\n'
                        f'CREG {max_qubit}\n'
                    )
                    originir += change_prep_base(inst_map,base,flip_base=flip_base)
                    originir += generate_pauli_twirl_circuit(inst_map,repeats=layer,cz_pattern=pattern)
                    originir += change_meas_base(inst_map,base,flip_base=flip_base)
                    measure_ir,ro_string = readout_twirl(inst_map,n_qubits)
                    circuit_data['{}_{}_ro_string'.format(index,count)] = ro_string
                    circuit_data['{}_{}_meas_base'.format(index,count)] = base
                    circuit_data['{}_{}_depth'.format(index,count)] = layer
                    originir += measure_ir
                    if not multi_txt:
                        originir +=(
                            f'//////////\n'
                        )
                    count += 1
                    if multi_txt:
                        filename = '{}_base_{}_dpeth_{}_cz_patter_{}_sample.txt'.format(base,layer,pattern,sample)
                        with open(output_path / filename, 'w') as fp:
                            fp.write(originir)
          
        circuit_data['num_of_{}_layer_circuits'.format(index)] = count
    if not multi_txt:    
        with open(output_path / 'originir.txt', 'w') as fp:
            fp.write(originir)
    
    with open('data.json', 'w') as fp:
        json.dump(circuit_data,fp)
        
        

    