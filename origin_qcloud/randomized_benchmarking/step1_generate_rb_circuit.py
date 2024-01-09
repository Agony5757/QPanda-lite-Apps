import json
from math import pi
import os
from pathlib import Path
import numpy as np
import rb_generator

from qpandalite.task.origin_qcloud import available_qubits
import qpandalite
from tqdm import tqdm


def from_1q_id_to_gate(qubit, operation_id, circuit : qpandalite.Circuit):
    if operation_id == 0:
        # circuit.identity(qubit)
        pass
    elif operation_id == 1:
        circuit.rphi(qubit, pi, 0)
    elif operation_id == 2:
        circuit.rphi(qubit, pi, pi/2)
    elif operation_id == 3:
        circuit.rphi(qubit, pi/2, 0)
    elif operation_id == 4:
        circuit.rphi(qubit, pi/2, pi/2)
    elif operation_id == 5:
        circuit.rphi(qubit, pi/2, pi)
    elif operation_id == 6:
        circuit.rphi(qubit, pi/2, 3*pi/2)
    else:
        raise ValueError('Invalid operation id')

def generate_circuit(rb22, qubits, length):
    circuit = qpandalite.Circuit()
    cliffords = np.random.randint(0, rb22.N, length)
    sequence, inverse_sequence = rb22.get_full_sequence_and_inverse_sequence(cliffords)
    # generate n_qubits of size length RB sequence and their inverse
    for qubit in qubits:
        for opid in sequence:
            from_1q_id_to_gate(qubit, opid, circuit)

        for opid in inverse_sequence:
            from_1q_id_to_gate(qubit, opid, circuit)
    
    circuit.measure(*qubits)

    return circuit.circuit


def generate_rb_groups(rb22, qubits, clifford_ranges, samples):
    circuits = []
    for i in tqdm(range(samples)):
        circuits += [generate_circuit(rb22, qubits, clifford_length) 
                     for clifford_length in clifford_ranges]
    return circuits

qubits = available_qubits
qubits = [30,31,32,33]
samples = 20

# Define the clifford length
clifford_lengths = list(range(2,10,2))+list(range(15,50,5))+list(range(60,100,10))+list(range(120,320,40))
if __name__ == '__main__':
    rb22 = rb_generator.RB22()
    # Open file first
    if not rb22.load_from_file('rb22.dat'): 
        print('load failed')
        exit(0)

    # if os.path.exists(Path.cwd() / f'rb_circuit_{qubits}.txt'):
    #     print('Use cached files. Nothing generated!')
    #     exit(0)

    circuits = generate_rb_groups(rb22, qubits, clifford_lengths, samples)  
    with open(Path.cwd() / f'rb_circuits.txt', 'w+') as fp:
        json.dump(circuits, fp)
    