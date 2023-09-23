import numpy as np
from itertools import product
import json
import requests
from qpandalite.task.originq import *
import pyqpanda as pq

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

savepath = Path.cwd() / 'online_info'
qv = [45,46,52,53,54,48]

if __name__ == '__main__':
    circuits = single_qubit_circuits(len(qv), qv)
    # circuits, theory, flip = double_gate_circuits(qv)
    taskid = submit_task(circuits, shots=1000,
                         task_name=f'test single gate qubit {qv}',
                         measurement_amend=False,
                         circuit_optimize=True,
                         auto_mapping=False,
                         savepath=savepath)
