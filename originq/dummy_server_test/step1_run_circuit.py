import numpy as np
import qpandalite.task.originq_dummy as originq
import scipy
X = np.array([[0,1],[1,0]])
m = scipy.linalg.expm(1j*X*(-1.402/2))
print(m)
c = '''
QINIT 3
CREG 3
RZ q[2],(1.5707963267948966)
CZ q[0],q[1]
X q[1]
H q[2]
RX q[1],(-1.5707963267948966)
RZ q[2],(1.5707963267948966)
CZ q[1],q[2]
RX q[1],(1.4020894648365463)
RX q[2],(1.4020894796568064)
CZ q[1],q[2]
MEASURE q[0],c[0]
MEASURE q[1],c[1]
MEASURE q[2],c[2]
'''
taskid = originq.submit_task(c, shots = 1000, auto_mapping=False)
results = originq.query_by_taskid(taskid)
print(results)