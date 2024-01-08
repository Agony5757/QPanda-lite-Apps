import json
import os
from pathlib import Path

path = Path.cwd() / 'output_noise_data' / 'noise_data.json'

with open(path, 'r') as fp:
    data = json.load(fp)
    data = data[0]
    fidelities = data['spam_noise']
    qubit_list = data['qubit_list']

def convert_basis_to_readable_format(pauli, qubit_list):
    pauli_list = list(pauli)
    ret = ''
    for i, p in enumerate(pauli_list):
        if p == 'I': 
            continue
        else:
            ret += f'{p}_{{{qubit_list[i]}}}'
    
    return ret

fidelity_data = []

for pauli in fidelities:
    readable_basis = convert_basis_to_readable_format(pauli, qubit_list)
    fidelity_data.append((readable_basis, fidelities[pauli]))

fidelity_data.sort(key=lambda pair:pair[1])

def make_color(fid):
    if fid < 0.8:
        return 'red'
    if 0.8 <= fid < 0.92:
        return 'gold'
    if fid >= 0.92:
        return 'green'

x = [i for i in range(len(fidelity_data))]
y = [pair[1] for pair in fidelity_data]
label = [f'${pair[0]}$' for pair in fidelity_data]
# color = [make_color(pair[1]) for pair in fidelity_data]

import matplotlib.pyplot as plt
plt.figure(dpi=200,figsize=[10,3])
plt.xticks(x, label, rotation=75)
plt.bar(x, y)
# plt.ylim([0.5,1])
plt.xlabel('Basis')
plt.ylabel('SPAM Error')
plt.show()

