import numpy as np
import qpandalite
import qpandalite.task.origin_qcloud as originq
from step1_generate_rb_circuit import qubits, samples, clifford_lengths
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
        print('status = ', results['status'])
        exit(0)

    results = results['result']

    results = qpandalite.convert_originq_result(results, 
                                                style='list',
                                                prob_or_shots='prob',
                                                key_style='bin')

    cliffords_results = None
    qubit_num = len(qubits)

    hamiltonians = ['I'* n + 'Z' + 'I' * (qubit_num - 1 - n) for n in range(qubit_num)]
    all_points = None

    for i, clifford_length in enumerate(clifford_lengths):
        total_expectations = np.zeros(qubit_num)
        for j in range(samples):
            exp_id = j * len(clifford_lengths) + i
            result = results[exp_id]
            
            expectations = qpandalite.calculate_expectation(result, hamiltonians)
            total_expectations += np.array(expectations)
            if all_points is None:
                all_points = np.array(expectations)
            else:
                all_points = np.vstack((all_points, expectations))

        total_expectations /= samples
        if cliffords_results is None:
            cliffords_results = total_expectations
        else:
            cliffords_results = np.vstack((cliffords_results, total_expectations))        

    print(qubit_num)
    for i in range(qubit_num):
        plt.figure()
        plt.plot(clifford_lengths, cliffords_results[:, i])
        a0, p = fit_rb(clifford_lengths, cliffords_results[:, i])
        plt.plot(clifford_lengths, exp_decay(np.array(clifford_lengths), a0, p), label = 'fit')
        # plt.scatter(clifford_lengths * samples, all_points[:, i])
        plt.title(f'Qubit {qubits[i]} A={a0}, F={p}')
        plt.savefig(f'Q{qubits[i]}.png', bbox_inches = 'tight')
        # plt.show()


