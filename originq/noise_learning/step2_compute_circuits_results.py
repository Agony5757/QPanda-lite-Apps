from backend import simulate_backend
from pathlib import Path
import os
import json
from task import load_circuit, load_circuit_group, submit_task, submit_task_group, default_task_group_size

def split_and_submit_group(circuits, shots, is_amend, circuit_optimize, confirm_count = 4):
    
    if len(circuits) <= default_task_group_size:
        filename = 'Noise-learning'
        response = submit_task_group(circuit=circuits, shots = shots, task_name=filename, measurement_amend=is_amend)
        print(filename, 'OK')
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
            response = submit_task_group(circuits=group, shots=shots, circuit_optimize = circuit_optimize,
                                            task_name=filename, measurement_amend=is_amend)
            print(filename, 'OK')
            
if __name__ == '__main__':
       
    is_amend = False
    shots = 256
    circuit_optimize = True

    # Mode = 'Simulation'
    # Mode = 'Multi-Txt'
    Mode = 'Single-Txt'

    if Mode == 'Simulation':
        n_qubits = 6
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