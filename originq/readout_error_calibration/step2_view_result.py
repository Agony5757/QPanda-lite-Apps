import json
import os
from pathlib import Path
from qpandalite.task.originq import *
import matplotlib.pyplot as plt
from itertools import product
import numpy as np
import seaborn as sns

from step1_circuits import savepath, qv

def plot(results, qubit_number):
    all_string = product([0, 1], repeat=qubit_number)
    plot_table = np.zeros((2**qubit_number, 2**qubit_number))
    for index, result in enumerate(results):
        for key, items in result.items():
            new_index = np.binary_repr(index, 6)[::-1]
            new_index = int(new_index, 2)
            plot_table[new_index, int(key, 2)] = items / 1000
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
    online_info = load_all_online_info(savepath=savepath)
    query_all_task(savepath=savepath)

    not_finished = []

    for task in online_info:
        taskid = task['taskid']
        taskname = '' if 'taskname' not in task else task['taskname']
        if not os.path.exists(savepath / f'{taskid}.txt'):
            not_finished.append({'taskid': taskid, 'taskname': taskname})

    if not_finished:
        print('Unfinished task list')
        for task in not_finished:
            taskid = task['taskid']
            taskname = task['taskname'] if task['taskname'] else 'null'
            print(f'  taskid:{taskid}, taskname:{taskname}')
        print(f'Unfinished: {len(not_finished)}')
    else:
        all_result = {}
        for i, task in enumerate(online_info):
            result_my = []
            taskid = task['taskid']
            taskname = task['taskname']
            print(f'Taskid: {taskid}')
            with open(savepath / f'{taskid}.txt') as fp:
                taskinfo = json.load(fp)

            if taskinfo['status'] == 'failed':
                continue

            result_list = taskinfo["result"]

            for result in result_list:
                keys = result['key']
                values = result['value']
                result_dict = {keys[i]: values[i] for i in range(len(keys))}
                result_my.append(result_dict)

            all_result[taskname] = result_my
            table = plot(all_result[taskname], 6)