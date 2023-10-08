import os
import subprocess
import sys
from datetime import datetime
import hashlib
import time
from memory_profiler import profile
import psutil

# set for March 2023 comp. MUST CHANGE
PROBLEM_COUNT = 10

# show usage if no solution file is provided
if (
    len(sys.argv) < 3
    or sys.argv[1] == "-h"
    or sys.argv[1] == "--help"
    or not sys.argv[1].isdigit()
    or int(sys.argv[1]) > PROBLEM_COUNT
):
    print("Usage: python3 grader.py [problem number] <solution_file>")
    print("For example, for the test problem: python3 grader.py 0 sum.py")
    exit()

problem_number = sys.argv[1]
solution_file = problem_number + "/" + sys.argv[2]  # The path to the solution file


def score(n, total_runtime, total_memory) -> int:
    """_summary_

    Args:
        n (int): number of test cases the solution was tested on
        total_runtime (float): total time for solution to run all test cases
        total_memory (float): total memory usage for solution to run all test cases

    Returns:
        int: The total score for the solution, after all test cases
    """
    
    runtime = total_runtime / n
    memory = total_memory / n
    
    # from math import log

    # # calculate score based on attempts, difficulty, and time

    # # for debugging
    # print(f"attempts: {attempts} \nbase: {base_score} \ntime: {time}s")
    
    # # subtract base_score/5 each time an incorrect attempt is made
    # score = base_score - ((attempts - 1) * (base_score / 5))
    
    # # if the time taken is above a dynamic difficulty threshold
    # if time > (base_score * 24):

    #     # the score is multiplied by a curve that accounts for time taken and starts at the threshold
    #     score = score * ((-(log(time - (24 * base_score - 20)) - 8) / 5))

    # # return a minimum score of 1 for a correct answer
    # if score < 1:
    #     return 1
    # else: 
    #     return round(score)
    

def grade(n):
    # determine the language based on the file extension
    ext = os.path.splitext(solution_file)[1]
    if ext == ".c":
        lang = "C"
        compile_cmd = ["gcc", "-o", "solution", solution_file]
        run_cmd = ["./solution"]
    elif ext == ".cpp":
        lang = "C++"
        compile_cmd = ["g++", "-o", "solution", solution_file]
        run_cmd = ["./solution"]
    elif ext == ".java":
        lang = "Java"
        compile_cmd = ["javac", solution_file]
        run_cmd = ["java", "Solution"]
    elif ext == ".py":
        lang = "Python"
        compile_cmd = None
        run_cmd = ["python3", solution_file]
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
    log = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Testing started at {log}")
    print(f"Security hash: {hashlib.sha256(log.encode()).hexdigest()}")
    
    # init number of correct test cases
    correct = 0

    for i in range(1, n + 1):
        input_file = f"./{problem_number}/{i}.in"
        output_file = f"./{problem_number}/{i}.out"

        print("-----------------------------")

        with open(input_file) as f_in:
            input_data = f_in.read()

            # # run the solution and capture its output
            # start_time = time.time()
            # result = subprocess.run(
            #     run_cmd, input=input_data.encode(), stdout=subprocess.PIPE
            # )
            # end_time = time.time()
            # # can put constraint on runtime if needed (ie. not exceeding 1 second)
            # runtime = end_time - start_time  

            # run the solution and capture its output
            start_time = time.time()
            process = subprocess.Popen(run_cmd, stdout=subprocess.PIPE)
            ps = psutil.Process(process.pid)
            output, errors = process.communicate(input=input_data.encode())

            # Wait for the process to finish and get the memory info
            process.wait()
            mem_info = ps.memory_info()
            end_time = time.time()

            # can put constraint on runtime if needed (ie. not exceeding 1 second)
            runtime = end_time - start_time  

            # Memory usage in bytes
            memory_usage = mem_info.rss

            if result.returncode != 0:
                print(f"✗ Solution crashed on test case {i} ✗")
                continue
            else:
                output_data = result.stdout.decode().strip()

            with open(output_file) as f_out:
                expected_output_data = f_out.read().strip()

            # compare test case with result
            if output_data == expected_output_data:
                print(f"Test case {i} PASSED")
                print(f"--> Output:\n{output_data}")
                print("--> Runtime:")
                print("{:.2f}s".format(runtime))
                correct += 1
            else:
                print(f"Test case {i} FAILED ✗")
                print(f"--> Expected:\n{expected_output_data}")
                print(f"--> Got:{output_data}")
            
    score()        
                
    print("-----------------------------")

    # cleanup: remove the compiled solution if present
    if compile_cmd:
        os.remove("solution")


@profile
def main():
    # count how many "n.in" files are in the directory ./problem_number/
    n = len(
        [
            name
            for name in os.listdir(problem_number)
            if os.path.isfile(os.path.join(problem_number, name))
            and name.endswith(".in")
        ]
    )
    grade(n)


main()
