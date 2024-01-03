from backend import simulate_backend
from pathlib import Path
import os
import json
from qpandalite import load_circuit, load_circuit_group
from qpandalite.task.originq import submit_task, default_task_group_size
from step1_generate_noise_lerning_circuits import available_qubits

default_task_group_size = 200

def split_and_submit_group(circuits, shots, is_amend, circuit_optimize, confirm_count = 4):
    
    if len(circuits) <= default_task_group_size:
        filename = 'Noise-learning'
        taskid = submit_task(circuit=list(circuits.values()), shots = shots, task_name=filename, measurement_amend=is_amend)
        print(f'Taskid: {taskid}, {filename}')
    else:
        groups = []
        group = []
        for circuit_name in circuits:
            if len(group) >= default_task_group_size:
                groups.append(group)
                group = []
            group.append(circuits[circuit_name])
        if group:
            groups.append(group)
        
        print('Number of groups: ', len(groups))
        for i, group in enumerate(groups):
            print('Group #{} size = {}'.format(i, len(group)))
            if confirm_count > 0:   
                input(f'Continue? Enter to confirm. (Remaining confirmation count = {confirm_count})')
                confirm_count -= 1

            filename = 'Noise-learning-{}'.format(i)
            taskid = submit_task(circuit=group, shots=shots, circuit_optimize = circuit_optimize,
                                            task_name=filename, measurement_amend=is_amend)
            print(f'Taskid: {taskid}, {filename}')
            
if __name__ == '__main__':
       
    is_amend = False
    shots = 500
    circuit_optimize = True

    # Mode = 'Simulation'
    # Mode = 'Multi-Txt'
    Mode = 'Single-Txt'

    if Mode == 'Simulation':
        qubit_limit = 20
        if len(available_qubits) > qubit_limit:
            raise NotImplementedError(f'Cannot simulate such large circuit (qubit > {qubit_limit}).')
        
        n_qubits = len(available_qubits)
        basepath = Path.cwd() / 'output_circuits'
        results = simulate_backend(basepath,n_qubits)
        output_path = Path.cwd() / 'output_results'
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        file_name = 'results.json'
        with open(output_path/file_name,'w') as fp:
            json.dump(results,fp)

    elif Mode == 'Multi-txt':
        basepath = Path.cwd() / 'output_circuits'
        circuits = load_circuit(basepath)

        split_and_submit_group(circuits, shots, is_amend, circuit_optimize)

    elif Mode == 'Single-Txt':
        path = Path.cwd() / 'output_circuits' / 'originir.txt'
        circuits = load_circuit_group(path)
        split_and_submit_group(circuits, shots, is_amend, circuit_optimize)
        
    print('All Ok! You can move on to step 3-1 ~~')