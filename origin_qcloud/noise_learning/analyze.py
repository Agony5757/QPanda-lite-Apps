from copy import deepcopy
import numpy as np
import scipy
import json
import os
from scipy.optimize import nnls
from termdata import TermData
from generate import TWIRL_GATES
from pathlib import Path

def untwirl_result(ro_string,result):
    ro_string = ro_string
    ro_untwirled = {}
    # ro_string = ro_string[::-1]
    for key in result:
        newkey = "".join([{'0':'1','1':'0'}[bit] if flip=="1" else bit for bit,flip in zip(key,ro_string)])
        ro_untwirled[newkey] = result[key]
    return ro_untwirled

'''
OLD
Note: the Pauli sequence is like

XYI, key:011, qubit_list=[45,46,52]

X = 52 (qubit_list[2]) = key[0]
Y = 46 (qubit_list[1]) = key[1]
I = 45 (qubit_list[0]) = key[2]
'''
def _get_expectation(pauli, result : dict):
    expectation_sum = 0
    for key in result:
        sgn = 1
        for i in range(len(key)):
            if pauli[i] != 'I' and key[i] == '1':
                sgn *= -1
        expectation_sum += sgn * result[key]
    
    expectation_sum = expectation_sum / sum(result.values())
    return expectation_sum

def get_expectation(pauli,ro_string,result):
    
    estimator = 0
    result = untwirl_result(ro_string,result)
    pz = []
    for p in pauli:
        if p =='I':
            pz.append('0')
        else:
            pz.append('1')
    #pz = pz[::-1]
    for key in result.keys():
        sgn = sum([{('1','1'):1}.get((pauli_bit, key_bit), 0) for pauli_bit, key_bit in zip(pz, key)])
        estimator += (-1)**sgn*result[key]
    
    estimator = estimator/sum(result.values())

    estimator_compare = _get_expectation(pauli, result)
    if estimator != estimator_compare:
        print(result, pauli)
        print(estimator_compare, estimator)
        raise RuntimeError('??')

    return estimator

def load_json(path):
    with open(path,'r') as fp:
        data = json.load(fp)
    return data

def simultaneous(pauli,other): 
    return all([p1==p2 or p2 == 'I' for p1,p2 in zip(pauli, other)])

def sim_meas(pauli,model_terms):
    simultaneous_meas = [term for term in model_terms if simultaneous(pauli,term)]
    return simultaneous_meas

def add_expectation(circuit_data,term_data,result):
    meas_base = circuit_data['meas_base']
    pair_sim_meas = {}
    depth = circuit_data['depth']
    model_terms = circuit_data['model_terms']
    ro_string = circuit_data['ro_string']
    if not meas_base in pair_sim_meas:
        pair_sim_meas[meas_base] = sim_meas(meas_base,model_terms=model_terms)
    
    for pauli in pair_sim_meas[meas_base]:
        expectation = get_expectation(pauli,ro_string,result)
        term_data[pauli].add_expectation(depth, expectation)
    
def fit_noise_model(term_data,ind, qubit_list):
    for index,term in enumerate(term_data.values()): 
        try:
            pauli = term.pauli
            term.fit()
            dir_name= Path.cwd()/'image'
            file_name = '{}_layer_{}.png'.format(pauli,ind)
            path = os.path.join(dir_name, file_name)
            os.makedirs(dir_name, exist_ok=True)
            term.graph(path, qubit_list)
            spam = term.spam
            fidelity = term.fidelity

        except RuntimeError as e:
            print(term.pauli, 'does not have available data, skipping.')            
        
    return nnls_fit(term_data)

def get_spam_coeffs(term_data):
    """Return a dictionary of the spam coefficients of different model terms for use in 
    readout error mitigation when PER is carried out."""

    return dict(zip(term_data.keys(), [termdata.spam for termdata in term_data.values()]))
    
def nnls_fit(term_data):

    def sprod(a,b):
        commute = True
        for char1,char2 in zip(a,b):
            if char1 == char2 or char1 =='I' or char2 == 'I':
               continue
            else:
                commute = False 
                break
        return (int)(not commute)

    F1 = [] 
    F2 = [] 
    fidelities = [] 

    for datum in term_data.values():
        F1.append(datum.pauli)
        fidelities.append(datum.fidelity)
        pair = datum.pair
        F2.append(pair)

    M1 = [[sprod(a,b) for a in F1] for b in F1]
    M2 = [[sprod(a,b) for a in F2] for b in F2]

    if np.linalg.matrix_rank(np.add(M1,M2)) != len(F1):
        raise Exception("Matrix is not full rank, something went wrong!")
    
    coeffs,_ = nnls(np.add(M1,M2), -.5*np.log(fidelities)) 
    return coeffs

def get_pauli_pair(pauli,pattern,mapping_info):
    conj_pauli = list(pauli)
    for pair in pattern:
        pauli_pair = (pauli[mapping_info[str(pair[0])]],pauli[mapping_info[str(pair[1])]])
        for x,y in TWIRL_GATES['cz']:
            if x == pauli_pair:
                conj_pauli[mapping_info[str(pair[0])]] = y[0]
                conj_pauli[mapping_info[str(pair[1])]] = y[1]
    return ''.join(conj_pauli)
        
def weight(pauli):
    return sum([p != "I" for p in pauli])

def analyze(circuit_data_path,result_path,verbose=False):
    """
    Noise_learning analysis 
    Args:
        circuit_data_path (str): circuit data path
        result_path (str): circuit result path
    Returns:
        None.  
    """
    if verbose:
        from tqdm import tqdm
    else:
        tqdm = lambda i : i
    circuit_data = load_json(circuit_data_path)
    data = {}
    data['model_terms'] = circuit_data['model_terms']
    patterns = circuit_data['cz_patterns']
    mapping_qubits = circuit_data['mapping_qubits']
    data['mapping_info'] = mapping_qubits
    qubit_list = [0]*len(mapping_qubits)
    for qubit in mapping_qubits:
        qubit_list[mapping_qubits[qubit]]=int(qubit)

    all_of_term_data_patterns = dict()
    noise_data_patterns = dict()
    results = load_json(result_path)
    count = 0 
    for i, pattern in enumerate(patterns):
        all_of_term_data = []
        noise_data = []
        num_of_circuit = circuit_data['num_of_{}_layer_circuits'.format(i)]
        term_data = {}
        for pauli in data['model_terms']:
            pair = get_pauli_pair(pauli,pattern,data['mapping_info'])
            term_data[pauli] = TermData(pauli, pair)
        for ind in tqdm(range(num_of_circuit)):
            data['ro_string'] = circuit_data['{}_{}_ro_string'.format(i,ind)] 
            data['meas_base'] = circuit_data['{}_{}_meas_base'.format(i,ind)]
            data['depth'] = circuit_data['{}_{}_depth'.format(i,ind)]
            add_expectation(data,term_data,results[count])
            count += 1
        all_of_term_data.append(term_data)
        
        for index,term_data in tqdm(enumerate(all_of_term_data)):
            noise_coeffes = {}
            coeffs = fit_noise_model(term_data,index,qubit_list)
            noise_coeffes['cz_pattern'] = patterns[index]
            noise_coeffes['coeffs'] = dict(zip(data['model_terms'],coeffs))        
            noise_coeffes['fidelity'] = {pauli: term_data[pauli].fidelity 
                                        for pauli in term_data}
            noise_coeffes['qubit_list'] = qubit_list
                
            noise_data.append(noise_coeffes)
        
        spam = {term:0 for term in data['model_terms'] if weight(term) == 1}
        
        for index,term_data in tqdm(enumerate(all_of_term_data)):
            spam_coeffs = get_spam_coeffs(term_data)
            for term in spam:
                spam[term] += spam_coeffs[term]/len(all_of_term_data)
            noise_data[index]['spam_noise'] = spam
        
        all_of_term_data_patterns[str(pattern)] = deepcopy(all_of_term_data)
        noise_data_patterns[str(pattern)] = deepcopy(noise_data)

    output_path = Path.cwd() / 'output_noise_data'
    
    if not os.path.exists(output_path):        
        os.makedirs(output_path)
        
    filename = 'noise_data.json'    
    noise_data_save_path = os.path.join(output_path,filename)  
    with open(noise_data_save_path,'w') as fp:
        json.dump(noise_data_patterns,fp)