from flask import Flask, request, render_template, redirect, flash
from werkzeug.utils import secure_filename
import os
import subprocess
import datetime
import gspread
from dotenv import load_dotenv

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEETS_ID = "1sAMe_4KNaX8qzPM7qvoDIBuw4d_Ul8xrpHNXBw51c7w"
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'py', 'c', 'cpp', 'java'}
NUM_OF_PROBLEMS = 12

load_dotenv()

app = Flask(__name__)
app.secret_key = 'Nisttech #1'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.debug = True

gc = gspread.service_account_from_dict({
    "type": os.environ.get("type"),
    "project_id": os.environ.get("project_id"),
    "private_key_id": os.environ.get("private_key_id"),
    "private_key" : os.environ.get("private_key").replace("\\n", "\n"),
    "client_email": os.environ.get("client_email"),
    "client_id": os.environ.get("client_id"),
    "auth_uri": os.environ.get("auth_uri"),
    "token_uri": os.environ.get("token_uri"),
    "auth_provider_x509_cert_url": os.environ.get("auth_provider_x509_cert_url"),
    "client_x509_cert_url": os.environ.get("client_x509_cert_url"),
    "universe_domain": os.environ.get("universe_domain")
})

sh = gc.open_by_key('1sAMe_4KNaX8qzPM7qvoDIBuw4d_Ul8xrpHNXBw51c7w')
worksheet = sh.sheet1

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def update_spreadsheet(timestamp, email, name, problem, file, output):
    try:
        data = worksheet.get_all_records()
        print(data)
    except gspread.exceptions.APIError as e:
        print(f"Error updating spreadsheet: {e}")
    
    timestamp_str = timestamp.isoformat()

    append_data = [timestamp_str, email, name, problem, file, output]
    worksheet.append_row(append_data)
    return


def valid_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS

@app.route("/", methods = ["POST", "GET"])
def index():
    if request.method == "GET":
        return render_template("index.html", NUM_OF_PROBLEMS=NUM_OF_PROBLEMS)
    elif request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        problem_num = request.form.get("prob_num")

        if problem_num == '':
            flash('No problem selected')
            return redirect("/")
        
        if problem_num.isdigit() == False:
            flash('Choose a number')
            return redirect("/")
        
        if problem_num > NUM_OF_PROBLEMS or problem_num < 0:
            flash("Invalid number")
            return redirect("/")
        
        if 'code' not in request.files:
            flash('No file part')
            return redirect("/")
        
        code = request.files["code"]

        if code.filename == '':
            flash('No selected file')
            return redirect("/")
        
        if code and valid_file(code.filename):
            filename = secure_filename(code.filename)
            code_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            code.save(code_path)
            return redirect("/results?problem_num=" + problem_num + "&filename=" + filename + "&name=" + name + "&email=" + email + "&code_path=" + code_path)
        else:
            flash("Invalid file type")
            return redirect("/")
        
@app.route("/results")
def results():
    problem_num = request.args.get("problem_num")
    filename = request.args.get("filename")
    name = request.args.get("name")
    email = request.args.get("email")
    code_path = request.args.get("code_path")

    fo = open(code_path, "r")
    code_content = fo.read() 
    fo.close()
    
    COMMAND = ["python3", "grader.py", problem_num, filename]
    
    result = subprocess.run(COMMAND, capture_output=True, text=True)

    errors = result.stderr
    output = result.stdout

    update_spreadsheet(datetime.datetime.now(), email, name, problem_num, code_content, output)

    return render_template("results.html", errors=errors, output=output, problem_num=problem_num)

def quicksort_leaderboard(arr):
    length = len(arr)
    if length <= 1:
        return arr
    else:
        pivot = arr.pop()
    
    items_greater = []
    items_lesser = []

    for item in arr:
        if item[1] > pivot[1]:
            items_greater.append(item)
        else:
            items_lesser.append(item)

    return quicksort_leaderboard(items_greater) + [pivot] + quicksort_leaderboard(items_lesser)

@app.route("/lb")
def leaderboard():
    leaderboard_sheet = sh.get_worksheet(1)
    leaderboard = []

    for i in range(5, 10):
        leaderboard.append([leaderboard_sheet.row_values(i)[2], int(leaderboard_sheet.row_values(i)[12])])

    leaderboard = quicksort_leaderboard(leaderboard)

    return render_template("leaderboard.html", leaderboard=leaderboard)