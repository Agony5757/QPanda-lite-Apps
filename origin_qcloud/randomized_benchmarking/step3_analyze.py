import numpy as np
import qpandalite
import qpandalite.task.originq as originq
from step1_generate_rb_circuit import available_qubits, samples, clifford_lengths
import matplotlib.pyplot as plt
import scipy.optimize

def exp_decay(x, A, p):
    return np.power(p, x) * A

def fit_rb(clifford_lengths, rb_results):
    fit_result, _ = scipy.optimize.curve_fit(exp_decay, clifford_lengths, rb_results, p0 = [1.0, 1.0])
    a0 = fit_result[0]
    p = fit_result[1]
    return a0, p

if __name__ == '__main__':
    taskid = originq.get_last_taskid()
    results = originq.query_by_taskid(taskid)

    if results['status'] != 'success':
        print('unfinished.')
        exit(0)

    results = results['result']

    results = qpandalite.convert_originq_result(results, 
                                                style='keyvalue',
                                                prob_or_shots='prob')

    cliffords_results = []
    qubit_num = len(available_qubits)

    hamiltonians = ['I'* n + 'Z' + 'I' * (qubit_num - 1 - n) for n in qubit_num]
    all_points = {}

    for i, clifford_length in enumerate(clifford_lengths):
        total_expectations = np.zeros(qubit_num)
        for j, sample in enumerate(samples):
            exp_id = j * len(clifford_lengths) + i
            result = results[exp_id]
            
            expectations = qpandalite.calculate_expectation(result, hamiltonians)
            total_expectations += np.array(expectations)
            if not all_points:
                all_points = np.array(expectations)
            else:
                all_points = np.vstack(all_points, expectations)

        total_expectations /= len(samples)
        if not cliffords_results:
            cliffords_results = total_expectations
        else:
            cliffords_results = np.vstack(cliffords_results, total_expectations)        

    for i in range(len(qubit_num)):
        plt.figure()
        plt.plot(clifford_lengths, cliffords_results[:, i])
        a0, p = fit_rb(clifford_lengths, cliffords_results[:, i])
        plt.plot(clifford_lengths, exp_decay(np.array(clifford_length)), label = 'fit')
        plt.scatter(clifford_lengths * samples, all_points[:, i])
        plt.title(f'Qubit {available_qubits[i]} A={a0}, F={p}')
        plt.savefig(f'Q{available_qubits[i]}.png', bbox_inches = 'tight')


