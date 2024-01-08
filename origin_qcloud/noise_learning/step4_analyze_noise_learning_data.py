from analyze import analyze
from pathlib import Path
import os
import json
import matplotlib
matplotlib.use('Agg')


if __name__ == '__main__':
    basepath = Path.cwd()
    circuit_data_path = os.path.join(basepath,'data.json')
    results_path = os.path.join(basepath,'output_results/results.json')  
    analyze(circuit_data_path,results_path,verbose=True)