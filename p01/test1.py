#!/bin/python

import argparse
import subprocess
from time import sleep
import time

parser = argparse.ArgumentParser(description='Test jfp solver.')
parser.add_argument('start', metavar='START', type=int)
parser.add_argument('end', metavar='END', type=int)

args = parser.parse_args()

for i in range(args.start, args.end + 1):
    print("Running for", i)

    generator = subprocess.run(['./gen_jss.py', str(i), str(i), '1', str(i), '1', str(i)], capture_output=True)
    problem = generator.stdout

    with open('.problem' + str(i) + ".jfp", 'w') as file:
        file.write(problem.decode('ascii'))

    mainp = subprocess.Popen('./main.py', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, restore_signals=False)
    
    start = time.time()
    main_out, _ = mainp.communicate(input=problem)
    end = time.time()

    main_out = main_out.decode('ascii')
    
    print("\t\tmain:\t", main_out.split('\n')[0])
    print("\t\ttook", end - start)
    
