import os
import subprocess
import sys
from datetime import datetime
import hashlib
import time
from memory_profiler import profile

# set for March 2023 comp. MUST CHANGE
PROBLEM_COUNT = 9

# show usage if no solution file is provided
if len(sys.argv) < 3 or sys.argv[1] == '-h' or sys.argv[1] == '--help' or not sys.argv[1].isdigit() or int(sys.argv[1]) > PROBLEM_COUNT:
        print("Usage: python3 grader.py [problem number] <solution_file>")
        print("For example, for the test problem: python3 grader.py 0 sum.py")
        exit()
        
problem_number = sys.argv[1]
solution_file = problem_number + '/' + sys.argv[2]  # The path to the solution file

def grade(n):
    # determine the language based on the file extension
    ext = os.path.splitext(solution_file)[1]
    if ext == '.c':
        lang = 'C'
        compile_cmd = ['gcc', '-o', 'solution', solution_file]
        run_cmd = ['./solution'] 
    elif ext == '.cpp':
        lang = 'C++'
        compile_cmd = ['g++', '-o', 'solution', solution_file]
        run_cmd = ['./solution']
    elif ext == '.java':
        lang = 'Java'
        compile_cmd = ['javac', solution_file]
        run_cmd = ['java', 'Solution']
    elif ext == '.py':
        lang = 'Python'
        compile_cmd = None
        run_cmd = ['python3', solution_file]
    else:
        print(f"Unsupported language: {ext}")
        return

    # compile the solution (if necessary)
    if compile_cmd:
        print(f"\033[1m\033[33mCompiling {lang} solution...\033[0m")
        result = subprocess.run(compile_cmd)
        if result.returncode != 0:
            print(f"\033[1m\033[91m✗ Failed to compile {lang} solution ✗\033[0m")
            return
        
    # print current date and time and a hash
    log = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Testing started at {log}")
    print(f"Security hash: {hashlib.sha256(log.encode()).hexdigest()}")

    for i in range(1,n+1):
        input_file = f"./{problem_number}/{i}.in"
        output_file = f"./{problem_number}/{i}.out"
        
        print("-----------------------------")
        
        with open(input_file) as f:
            input_data=f.read()
            
            # run the solution and capture its output
            start_time = time.time()
            result=subprocess.run(run_cmd,input=input_data.encode(),stdout=subprocess.PIPE)
            end_time = time.time()
            runtime = end_time - start_time  # Can put constraint on runtime if needed (ie. not exceeding 1 second)

            if result.returncode!=0:
                print(f"✗ Solution crashed on test case {i} ✗")
                continue

            output_data=result.stdout.decode().strip()  
            
            f = open(output_file)
            expected_output_data=f.read().strip()
            f.close()
                
            # compare test case with result
            if output_data==expected_output_data:
                print(f"Test case {i} PASSED")
                print(f"--> Output:\n{output_data}")
                print("--> Runtime:")
                print("{:.2f}s".format( runtime ))
            else:
                print(f"Test case {i} FAILED ✗")
                print(f"--> Expected:\n{expected_output_data}")
                print(f"--> Got:{output_data}")
    print("-----------------------------")
    
    # cleanup: remove the compiled solution if present
    if compile_cmd:
        os.remove('solution')
    
# count how many "n.in" files are in the directory ./problem_number/
@profile
def main():
    n = len([name for name in os.listdir(problem_number) if os.path.isfile(os.path.join(problem_number, name)) and name.endswith(".in")])
    grade(n)

main()