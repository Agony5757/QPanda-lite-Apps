import json
import os
from pathlib import Path
from qpandalite.task.originq import *
import matplotlib.pyplot as plt
from itertools import product
import numpy as np
import seaborn as sns
import qpandalite

from step1_circuits import available_qubits

def plot(results, qubit_number):
    plot_table = np.zeros((2**qubit_number, 2**qubit_number))
    for index, result in enumerate(results):
        for key, items in result.items():
            plot_table[index, key] = np.log2(items)
    sns.heatmap(plot_table)
    plt.show()
    return plot_table

def flip_result(r, f):
    new_result = {}
    for key, value in r.items():
        new_key = ''.join([str(abs(int(key[i])-f[i])) for i in range(len(f))])
        new_result[new_key] = value
    return new_result

def double_qubit_check(result, theory, flip):
    plot_table = np.zeros((4, 4))
    new_result = [flip_result(result[i], flip[i]) for i in range(len(flip))]
    average_result = [new_result[4*i:4*i+4] for i in range(4)]
    s = ['00', '01', '10', '11']
    for i in range(4):
        average_result = dict(zip(s, [average_result[i][k][j] for j in s for k in range(4)]))
    pass


if __name__ == '__main__':
    taskid = get_last_taskid()
    results = query_by_taskid(taskid)
    # print(results)
    data = []
    
    if results['status'] != 'success':
        print('Not finished')
        exit(0)
    
    results = results['result']

    for result in results:
        data.append(qpandalite.convert_originq_result(result, 
                                                      style='keyvalue',
                                                      prob_or_shots='prob'))

    table = plot(data, len(available_qubits))