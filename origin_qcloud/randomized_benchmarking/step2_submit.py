
from qpandalite.task.origin_qcloud import submit_task
import json

with open('rb_circuits.txt', 'r') as fp:
    circuits = json.load(fp)

print(len(circuits), type(circuits))

input('Press Enter to confirm')

taskid = submit_task(circuits, 
                     auto_mapping=False, 
                     measurement_amend=False, 
                     circuit_optimize=False, 
                     task_name='RB')
print(taskid)