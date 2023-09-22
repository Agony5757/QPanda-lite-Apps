from task import load_all_online_info
from pathlib import Path
import json
import os

if __name__ == "__main__":
    
    savepath = Path.cwd() / 'online_info'
    online_info = load_all_online_info()
    output_path = Path.cwd() / 'output_results'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    file_name = 'results.json'
    results = []
    for task in online_info:
        taskid = task['taskid']
        with open(savepath / f'{taskid}.txt', 'r') as fp:
            taskinfo = json.load(fp)

        if taskinfo['status'] == 'failed':
            continue
        
        result_list = taskinfo["result"]

        for result in result_list:
            keys = result['key']
            values = result['value']
            result_dict = {keys[i][::-1]:values[i] for i in range(len(keys))}
            results.append(result_dict)
            
    with open(output_path/file_name,'w') as fp:
        json.dump(results,fp)