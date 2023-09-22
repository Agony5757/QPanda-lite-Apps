from task import load_all_online_info, query_all_task
import json
from pathlib import Path
import os

if __name__ == "__main__":
    savepath = Path.cwd() / 'online_info'
    online_info = load_all_online_info()

    query_all_task()

    not_finished = []
    
    for task in online_info:
        taskid = task['taskid']
        taskname = '' if 'taskname' not in task else task['taskname']
        if not os.path.exists(savepath / f'{taskid}.txt'):
            not_finished.append({'taskid':taskid, 'taskname':taskname})

    if not_finished:
        print('Unfinished task list')
        for task in not_finished:
            taskid = task['taskid']
            taskname = task['taskname'] if task['taskname'] else 'null'
            print(f'  taskid:{taskid}, taskname:{taskname}')
        print(f'Unfinished: {len(not_finished)}')    
    else:
        print('All Ok! You can move on to step 4 ~~')