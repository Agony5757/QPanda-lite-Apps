from qpandalite.task.originq import load_all_online_info, query_all_task
from pathlib import Path
import json
import qpandalite
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
            result_dict = qpandalite.convert_originq_result(result, 
                                                            style='keyvalue', 
                                                            prob_or_shots='prob',
                                                            key_style='bin')
            results.append(result_dict)
            
    with open(output_path/file_name,'w') as fp:
        json.dump(results,fp)