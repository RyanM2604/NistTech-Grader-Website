from flask import Flask, request, render_template, redirect, flash
from werkzeug.utils import secure_filename
import os
import subprocess
import datetime
import gspread

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEETS_ID = "1sAMe_4KNaX8qzPM7qvoDIBuw4d_Ul8xrpHNXBw51c7w"
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'py', 'c', 'cpp', 'java'}
NUM_OF_PROBLEMS = 12

app = Flask(__name__)
app.secret_key = 'Nisttech #1'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.debug = True

gc = gspread.service_account(filename='gsheet_credentials.json')

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