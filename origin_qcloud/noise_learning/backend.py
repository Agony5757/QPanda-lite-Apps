import pyqpanda as pq
import json
import os
USE_CHIP = False

def load_circuits_originir(path):
    ir_path = os.path.join(path,'originir.txt')
    print(ir_path)
    with open(ir_path,'r') as fp:
        circuits = fp.read()
    return circuits

def generate_binary_keys(n):
    binary_strings = []
    num_strings = 1 << n
    for i in range(num_strings):
        binary_string = format(i, f'0{n}b')
        binary_strings.append(binary_string)
    return binary_strings

def get_noise_nodel():
    noise = pq.Noise()
    noise.add_noise_model(pq.NoiseModel.DEPOLARIZING_KRAUS_OPERATOR, pq.GateType.CZ_GATE, 0.05)
    f0 = 0.9
    f1 = 0.85
    noise.set_readout_error([[f0, 1 - f0], [1 - f1, f1]])
    #noise.add_noise_model(pq.NoiseModel.DEPHASING_KRAUS_OPERATOR, pq.GateType.CZ_GATE, 0.1)
    #noise.add_noise_model(pq.NoiseModel.DAMPING_KRAUS_OPERATOR, pq.GateType.CZ_GATE, 0.1)
    return noise

def simulate_backend(path,n_qubits):
    """
        Simulation
    Args:
        path (str): output_circuits path
        n_qubits (int, optional): if use qvm, must give number of qubits. 

    Returns:
        None
    """
    qvm = pq.CPUQVM()
    qvm.init_qvm()
    q = qvm.qAlloc_many(n_qubits)
    c= qvm.cAlloc_many(n_qubits)
    circuits = load_circuits_originir(path)
    circuit_lines = circuits.split('/'*10+'\n')
    results = []
    noise_model = get_noise_nodel()
    for ir in circuit_lines:
        if ir:
            prog,q,c = pq.convert_originir_str_to_qprog(ir,qvm)
            prob = qvm.run_with_configuration(prog,c,shot=256,noise_model=noise_model)
            results.append(prob)
    return results

def real_chip_backend(path):
    
    pass
     
    
        
    