# VERIFY THE BIT SEQUENCE !!!

from pathlib import Path
import qpandalite
from qpandalite.task.origin_qcloud import *

circuit_1 = \
'''
QINIT 72
CREG 6
H q[0]
H q[1]
MEASURE q[0],c[0]
MEASURE q[1],c[1]
MEASURE q[2],c[2]
MEASURE q[8],c[3]
MEASURE q[7],c[4]
MEASURE q[6],c[5]
'''.strip()

circuit_2 = \
'''
QINIT 72
CREG 6
H q[0]
H q[1]
H q[2]
MEASURE q[0],c[0]
MEASURE q[1],c[1]
MEASURE q[2],c[2]
MEASURE q[8],c[3]
MEASURE q[7],c[4]
MEASURE q[6],c[5]
'''.strip()

circuit_3 = \
'''
QINIT 72
CREG 6
H q[0]
H q[1]
H q[2]
H q[8]
MEASURE q[0],c[0]
MEASURE q[1],c[1]
MEASURE q[2],c[2]
MEASURE q[8],c[3]
MEASURE q[7],c[4]
MEASURE q[6],c[5]
'''.strip()

circuit_4 = \
'''
QINIT 72
CREG 6
H q[0]
H q[1]
H q[2]
H q[8]
H q[7]
MEASURE q[0],c[0]
MEASURE q[1],c[1]
MEASURE q[2],c[2]
MEASURE q[8],c[3]
MEASURE q[7],c[4]
MEASURE q[6],c[5]
'''.strip()

circuit_5 = \
'''
QINIT 72
CREG 6
H q[0]
H q[1]
H q[2]
H q[8]
H q[7]
H q[6]
MEASURE q[0],c[0]
MEASURE q[1],c[1]
MEASURE q[2],c[2]
MEASURE q[8],c[3]
MEASURE q[7],c[4]
MEASURE q[6],c[5]
'''.strip()

circuit_6 = \
'''
QINIT 72
CREG 6
H q[0]
CNOT q[0], q[1]
MEASURE q[0],c[0]
MEASURE q[1],c[1]
MEASURE q[2],c[2]
MEASURE q[8],c[3]
MEASURE q[7],c[4]
MEASURE q[6],c[5]
'''.strip()

circuit_7 = \
'''
QINIT 72
CREG 6
H q[0]
CNOT q[0],q[1]
CNOT q[1],q[2]
MEASURE q[0],c[0]
MEASURE q[1],c[1]
MEASURE q[2],c[2]
MEASURE q[8],c[3]
MEASURE q[7],c[4]
MEASURE q[6],c[5]
'''.strip()

circuit_8 = \
'''
QINIT 72
CREG 6
H q[0]
CNOT q[0],q[1]
CNOT q[1],q[2]
CNOT q[2],q[8]
MEASURE q[0],c[0]
MEASURE q[1],c[1]
MEASURE q[2],c[2]
MEASURE q[8],c[3]
MEASURE q[7],c[4]
MEASURE q[6],c[5]
'''.strip()

circuit_9 = \
'''
QINIT 72
CREG 6
H q[0]
CNOT q[0],q[1]
CNOT q[1],q[2]
CNOT q[2],q[8]
CNOT q[8],q[7]
MEASURE q[0],c[0]
MEASURE q[1],c[1]
MEASURE q[2],c[2]
MEASURE q[8],c[3]
MEASURE q[7],c[4]
MEASURE q[6],c[5]
'''.strip()

circuit_10 = \
'''
QINIT 72
CREG 6
H q[0]
CNOT q[0],q[1]
CNOT q[1],q[2]
CNOT q[2],q[8]
CNOT q[8],q[7]
CNOT q[7],q[6]
MEASURE q[0],c[0]
MEASURE q[1],c[1]
MEASURE q[2],c[2]
MEASURE q[8],c[3]
MEASURE q[7],c[4]
MEASURE q[6],c[5]
'''.strip()

circuits = [circuit_1, circuit_2, circuit_3, circuit_4, circuit_5, 
            circuit_6, circuit_7, circuit_8, circuit_9, circuit_10]

if __name__ == '__main__':
    
    taskid = submit_task(circuits, 
                        shots=1000, 
                        task_name='Verify', 
                        circuit_optimize=True,
                        auto_mapping=False)
    print(f'taskid: {taskid}')
