import requests
from pathlib import Path
import os
import json

default_token = 'B356553132EB462C'
default_url = 'https://10.10.7.99:10080'
default_task_group_size = 200


def load_circuit(basepath = None):
    circuits = dict()
    if not basepath:
        basepath = Path.cwd() / 'output_circuits'

    files = os.listdir(basepath)    
    
    for file in files:
        if file.endswith('txt'):
            with open(basepath / file, 'r') as fp:
                circuit_text = fp.read()
            circuits[file] = circuit_text

    return circuits

def load_circuit_group(path = None):
    circuits = dict()
    if not path:
        path = Path.cwd() / 'output_circuits' / 'originir.txt'

    with open(path, 'r') as fp:
        circuit_text = fp.read()

    originirs = circuit_text.split('//////////')
    for i, originir in enumerate(originirs):
        stripped = originir.strip()
        if stripped and stripped.startswith('QINIT'):
            circuits[i] = stripped

    return circuits

def parse_query_circuit(response_body):

    ret = dict()
    ret['taskid'] = response_body['taskId']
    ret['taskname'] = response_body['taskDescribe']

    task_status = response_body['taskState']
    if task_status == '3':
        # successfully finished !
        ret['status'] = 'success'

        # task_result
        task_result = response_body['taskResult']
        task_result = json.loads(task_result)
        ret['result'] = task_result

        return ret
    elif task_status == '4':
        ret['status'] = 'failed'
        ret['result'] = {'errcode' : response_body['errCode'], 'errinfo': response_body['errInfo']}

        return ret
    else:
        ret['status'] = 'running'
        return ret

def query_circuit_status(taskid = None, baseurl = default_url):
    '''query_circuit_status

    Returns:
        - {'status': str, 'result': dict}
        status : success | failed | running
        result (when success): 
        result (when failed): {'errcode': str, 'errinfo': str}
        result (when running): N/A
    '''
    if not taskid: raise RuntimeError('Task id ??')
    
    baseurl = 'http://10.10.7.99:5000'
    url = baseurl + '/test-api//management/query/taskinfo'
    # url = baseurl + '/task/realQuantum/query'

    # construct request_body for task query
    request_body = dict()
    request_body['token'] = default_token
    request_body['taskid'] = taskid

    request_body = json.dumps(request_body)
    response = requests.post(url=url, data=request_body, verify = False)
    status_code = response.status_code
    if status_code != 200:
        print(response)
        print(response.text)
        raise RuntimeError('Error in query_circuit_status')
    
    text = response.text
    response_body = json.loads(text)

    taskinfo = parse_query_circuit(response_body)

    return taskinfo

def submit_task(circuit = None, 
                task_name = None, 
                tasktype = None, 
                chip_id = 72,
                shots = 1000,
                circuit_optimize = True,
                measurement_amend = True,
                auto_mapping = False,
                specified_block = None,
                baseurl = default_url,
                savepath = Path.cwd() / 'online_info'
):
    '''submit_task

    Returns:
        - dict : {'status': task_status, 'taskid': task_id}
    '''
    if not circuit: raise RuntimeError('circuit ??')
    # url = baseurl + '/test-api//task/realQuantum/run'
    url = baseurl + '/task/realQuantum/run'

    # construct request_body for task query
    request_body = dict()
    request_body['token'] = default_token
    request_body['ChipID'] = chip_id
    request_body['taskDescribe'] = task_name if task_name is not None else 'qpandalite' # 'Default info'
    request_body['QMachineType'] = tasktype if tasktype is not None else "5"
    request_body['TaskType'] = 0
    request_body['QProg'] = [circuit]
    
    configuration = dict()
    configuration['shot'] = shots
    configuration['circuitOptimization'] = circuit_optimize
    configuration['amendFlag'] = measurement_amend
    configuration['mappingFlag'] = auto_mapping
    configuration['specified_block'] = specified_block if specified_block is not None else []

    request_body['Configuration'] = configuration

    request_body = json.dumps(request_body)  

    response = requests.post(url=url, data=request_body, verify = False)
    status_code = response.status_code
    if status_code != 200:
        print(response)
        print(response.text)
        raise RuntimeError('Error in submit_task')
    
    try:
        text = response.text
        response_body = json.loads(text)
        task_status = response_body['taskState']
        task_id = response_body['taskId']
        ret = {'taskid': task_id, 'taskname': task_name}
    except Exception as e:
        print(response_body)
        raise e

    if savepath:
        make_savepath(savepath)
        with open(savepath / 'online_info.txt', 'a') as fp:
            fp.write(json.dumps(ret) + '\n')
    return ret



def submit_task_group(circuits = None, 
                task_name = None, 
                tasktype = None, 
                chip_id = 72,
                shots = 1000,
                circuit_optimize = True,
                measurement_amend = True,
                auto_mapping = False,
                specified_block = None,
                baseurl = default_url,
                savepath = Path.cwd() / 'online_info'
):
    '''submit_task

    Returns:
        - dict : {'status': task_status, 'taskid': task_id}
    '''
    if not circuits: raise RuntimeError('circuit ??')
    if len(circuits) > default_task_group_size:
        raise RuntimeError(f'Circuit group size too large. '
                           f'(Expect: <= {default_task_group_size}, Get: {len(circuits)})')

    # url = baseurl + '/test-api//task/realQuantum/run'
    url = baseurl + '/task/realQuantum/run'

    # construct request_body for task query
    request_body = dict()
    request_body['token'] = default_token
    request_body['ChipID'] = chip_id
    request_body['taskDescribe'] = task_name if task_name is not None else 'qpandalite' # 'Default info'
    request_body['QMachineType'] = tasktype if tasktype is not None else "5"
    request_body['TaskType'] = 0
    request_body['QProg'] = circuits
    
    configuration = dict()
    configuration['shot'] = shots
    configuration['circuitOptimization'] = circuit_optimize
    configuration['amendFlag'] = measurement_amend
    configuration['mappingFlag'] = auto_mapping
    configuration['specified_block'] = specified_block if specified_block is not None else []

    request_body['Configuration'] = configuration

    request_body = json.dumps(request_body)  
    
    response = requests.post(url=url, data=request_body, verify = False)
    status_code = response.status_code
    if status_code != 200:
        print(response)
        print(response.text)
        raise RuntimeError('Error in submit_task')
    
    try:
        text = response.text
        response_body = json.loads(text)
        task_status = response_body['taskState']
        task_id = response_body['taskId']
        ret = {'taskid': task_id, 'taskname': task_name}
    except Exception as e:
        print(response_body)
        raise e

    if savepath:
        make_savepath(savepath)
        with open(savepath / 'online_info.txt', 'a') as fp:
            fp.write(json.dumps(ret) + '\n')
    return ret

def make_savepath(savepath = None):    
    if not savepath:
        savepath = Path.cwd() / 'online_info'

    if not os.path.exists(savepath):
        os.makedirs(savepath)

    if not os.path.exists(savepath / 'online_info.txt'):
        with open(savepath / 'online_info.txt', 'w') as fp:
            pass

def load_all_online_info(savepath = None): 
    if not savepath:
        savepath = Path.cwd() / 'online_info'
    online_info = []
    with open(savepath / 'online_info.txt', 'r') as fp:
        lines = fp.read().strip().splitlines()

        for line in lines:
            online_info.append(json.loads(line))

    return online_info       

def _write_taskinfo(savepath, taskid, taskinfo):
    with open(savepath / '{}.txt'.format(taskid), 'w') as fp:
        json.dump(taskinfo, fp)
 
def query_all_task(savepath = None, baseurl = default_url): 
    if not savepath:
        savepath = Path.cwd() / 'online_info'
    
    online_info = load_all_online_info(savepath)
    for task in online_info:
        taskid = task['taskid']
        if not os.path.exists(savepath / '{}.txt'.format(taskid)):
            taskinfo = query_circuit_status(taskid=taskid, baseurl=baseurl)
            if taskinfo['status'] == 'success' or taskinfo['status'] == 'failed':
                _write_taskinfo(savepath, taskid, taskinfo)
    
def _test_run_circuit():
    circuits = load_circuit()
    
    # options
    is_amend = True
    shots = 10000
    
    for filename in circuits:        
        response = submit_task(circuit = circuits[filename], shots = shots, task_name=filename, measurement_amend=is_amend)
        print(filename, 'OK')

def _test_query_one_task(taskid='80F9B2F63DC142DE9A22F9F8469EC816'):    
    response_text = query_circuit_status(taskid=taskid)
    print(response_text)

def _test_query_all_task():
    query_all_task()
    
if __name__ == '__main__':
    make_savepath()
    # _test_run_circuit()
    _test_query_all_task()
