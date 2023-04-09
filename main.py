from flask import Flask,Response,request,jsonify,render_template,redirect
import pymongo,json,jwt
from flask_bcrypt import Bcrypt
from datetime import datetime,timedelta
import pandas as pd
import flask_excel as excel


# Opening config file to change according to the user
with open('config.json','r') as c:
    params = json.load(c)['params']


app = Flask(__name__)
bcrypt = Bcrypt(app)
secret = "***************"

#connecting with mongodb server

try:
    host = params['host']
    port = params['port']
    timeout = params['timeout']
    mongo = pymongo.MongoClient(host=host,port=port,serverSelectionTimeoutMS=timeout)
    db = mongo.Attendance # Creates a database of Attendance
    mongo.server_info() # This will remind the server to check after the timeout and get info

except Exception as ex:
    print(ex)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth/<string:prof>')
def auth(prof):
    return render_template('auth.html',v=prof)

@app.route('/signup/<string:x>', methods=['POST'])
def save(x):
    message = ""
    code = 500
    status = "fail"
    try:
        admission_number = request.form['admin']
        password = request.form['password']
        data = {"admission_number":f"{admission_number}","password":f"{password}","subjects":[]}

        check = db[x].count_documents({"admission_number": data['admission_number']})
        if check>= 1:
            message = "user with that admission_number exists"
            code = 401
            status = "fail"
        else:
            # hashing the password so it's not stored in the db as it was 
            data['password'] = bcrypt.generate_password_hash(data['password'])
            data['created'] = datetime.now()

            res = db[x].insert_one(data) 
            if res.acknowledged:
                status = "successful"
                message = "user created successfully"
                code = 201
                if(x=="teacher"):
                    url = "/teacher/"+admission_number
                    return redirect(url)
                else:
                    url = "/student/"+admission_number
                    return redirect(url)
    except Exception as ex:
        message = f"{ex}"
        status = "fail"
        code = 500
    return jsonify({'status': status, "message": message}), 200

#Route to Login for students
@app.route('/login/<string:x>', methods=['POST'])
def login(x):
    message = ""
    res_data = {}
    code = 500
    status = "fail"
    try:
        admission_number = request.form['admin']
        password = request.form['password']
        data = {"admission_number":f"{admission_number}","password":f"{password}"}
        user = db[x].find_one({"admission_number": f'{data["admission_number"]}'})

        if user:
            user['_id'] = str(user['_id'])
            if user and bcrypt.check_password_hash(user['password'], data['password']):
                time = datetime.utcnow() + timedelta(hours=24)
                token = jwt.encode({
                        "user": {
                            "admission_number": f"{user['admission_number']}",
                            "id": f"{user['_id']}",
                        },
                        "exp": time
                    },secret)

                del user['password']

                message = f"user authenticated"
                code = 200
                status = "successful"
                res_data['token'] = token
                res_data['user'] = user
                if(x=="teacher"):
                    url = "/teacher/"+admission_number
                    return redirect(url)
                else:
                    url = "/student/"+admission_number
                    return redirect(url)

            else:
                message = "wrong password"
                code = 401
                status = "fail"
        else:
            message = "invalid login details"
            code = 401
            status = "fail"

    except Exception as ex:
        message = f"{ex}"
        code = 500
        status = "fail"
    return jsonify({'status': status, "data": res_data, "message":message}), code

@app.route("/teacher/<id>")
def teacher_dashboard(id):
    return render_template("teacher_dashboard.html",id=id)

@app.route("/student/<id>")
def student_dashboard(id):
    return render_template("student_dashboard.html",id=id)


@app.route("/teacher/<id>/new",methods=['POST','GET'])
def new_class(id):
    if request.method == 'POST':
        # professor_name = request.form['name']
        # camera_url = request.form['prof_name']
        # subject = request.form['subject']
        # subject_code = request.form['subject_code']
        f = request.files['excell']
        data_xls = pd.read_excel(f)
        data = data_xls.to_json(orient="records")
        db['class'].insert_many(data)
        return data
    return render_template("new_class.html",id=id)

@app.route("/tutorial")
def tutorial():
    return render_template('tutorial.html')
    
app.run(debug=True)