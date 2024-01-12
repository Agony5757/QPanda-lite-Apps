
from qpandalite.task.originq import submit_task
import json

with open('rb_circuit.txt', 'r') as fp:
    circuits = json.load(fp)

print(len(circuits), type(circuits))

taskid = submit_task(circuits, mapping=False, circuit_optimize=True, task_name='RB')
print(taskid)