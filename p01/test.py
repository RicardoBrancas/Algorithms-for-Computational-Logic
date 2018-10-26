#!/bin/python

import argparse
import subprocess

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

    mainp = subprocess.Popen('./main.py', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    googlep = subprocess.Popen('./google.py', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    main_out, _ = mainp.communicate(input=problem)
    google_out, _ = googlep.communicate(input=problem)

    main_out = main_out.decode('ascii')
    google_out = google_out.decode('ascii')
    
    mainp.wait()
    googlep.wait()

    if main_out.split('\n')[0] != google_out.split('\n')[0]:
        print("\tSolutions don't match")
        print("\t\tmain:\t", main_out.split('\n')[0])
        print("\t\tgoogle:\t", google_out.split('\n')[0])
    else:
        print("\tSolutions match!")
    
    
