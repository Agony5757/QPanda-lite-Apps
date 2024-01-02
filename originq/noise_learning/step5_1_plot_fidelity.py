import json
import os
from pathlib import Path

def convert_basis_to_readable_format(pauli, qubit_list):
    pauli_list = list(pauli)
    ret = ''
    for i, p in enumerate(pauli_list):
        if p == 'I': 
            continue
        else:
            ret += f'{p}_{{{qubit_list[i]}}}'
    
    return ret

def make_color(fid):
    if fid < 0.8:
        return 'red'
    if 0.8 <= fid < 0.92:
        return 'gold'
    if fid >= 0.92:
        return 'green'
    
path = Path.cwd() / 'output_noise_data' / 'noise_data.json'

with open(path, 'r') as fp:
    data_patterns = json.load(fp)
    for cz_pattern, data in data_patterns.items():       
        data = data[0] 
        fidelities = data['fidelity']
        qubit_list = data['qubit_list']
        fidelity_data = []

        for pauli in fidelities:
            readable_basis = convert_basis_to_readable_format(pauli, qubit_list)
            fidelity_data.append((readable_basis, fidelities[pauli]))

        fidelity_data.sort(key=lambda pair:pair[1])

        x = [i for i in range(len(fidelity_data))]
        y = [pair[1] for pair in fidelity_data]
        label = [f'${pair[0]}$' for pair in fidelity_data]
        color = [make_color(pair[1]) for pair in fidelity_data]

        import matplotlib.pyplot as plt
        plt.figure(dpi=180,figsize=[35,10])
        plt.xticks(x, label, rotation=75)
        plt.bar(x, y, color=color)
        plt.ylim([0.5,1])
        plt.xlabel('Basis')
        plt.ylabel('Fidelity')
        plt.title('CZ Pattern: {}'.format(cz_pattern))
        # plt.show()
        plt.savefig(f'{cz_pattern}-Fidelity.png', bbox_inches = 'tight')
