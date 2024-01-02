import numpy as np
from itertools import product
import json
import requests
from qpandalite.task.originq import *

def remap_ir(ir_str, chip_idx):
    dup_ir = ir_str
    for i in range(len(chip_idx)):
        dup_ir = dup_ir.replace('q[{}]'.format(i), 'q[{}]'.format(chip_idx[i]))
    return dup_ir

def single_qubit_circuits(qubit_number, qv):
    all_string = product([0, 1], repeat=qubit_number)
    circuits = []
    for string in all_string:
        circuit = 'QINIT 72\n'
        circuit += f'CREG {qubit_number}\n'
        for index, s in enumerate(string):
            if s == 1:
                circuit += f'X q[{qv[index]}]\n'
        for index in range(len(string)):
            circuit += f'MEASURE q[{qv[index]}], c[{index}]\n'
        circuits.append(circuit)
    return circuits

available_qubits = [0,1,2,3,6,7,8,9,10,11]
if __name__ == '__main__':
    circuits = single_qubit_circuits(len(available_qubits), available_qubits)
    # circuits, theory, flip = double_gate_circuits(qv)
    taskid = submit_task(circuits, shots=1000,
                         task_name=f'test single gate qubit {available_qubits}',
                         measurement_amend=False,
                         circuit_optimize=True,
                         auto_mapping=False)
