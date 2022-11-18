from flask import *
from flask_session import Session
from sql_calls import *
import ibm_db

app = Flask(__name__)
#connection database
con = ibm_db.connect("DATABASE=bludb; HOSTNAME=ba99a9e6-d59e-4883-8fc0-d6a8c9f7a08f.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud; PORT=31321; SECURITY=SSL; SSLServerCertificate=DigiCertGlobalRootCA.crt; UID=qxh83236; PWD=nNnU0FLB0HNnzAzZ",'','')

#login page
@app.route('/',methods=['POST','GET'])
def login():
    return render_template('login.html')

#register page
@app.route('/register')
def register():
    return render_template('register.html')

#dashboard page
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

#login_validator
@app.route('/login_validation',methods=['GET','POST'])
def login_validation():
    email=request.form.get('email'.lower())
    password=request.form.get('password')
    
    #checking for email and password in db
    if (check_query_data.check_two_column(c1='email',d1=email,c2='password',d2=password)):
        return render_template('dashboard.html')
    else:
        return render_template('login.html',invalid_msg='Invalid login credentials')

#register_validator
@app.route('/register_validation',methods=['GET','POST'])
def register_validation():
    name=request.form.get('name'.lower())
    company_name=request.form.get('company'.lower())
    email=request.form.get('email'.lower())
    password=request.form.get('password')
    
    #checks already email and company_name exist in db
    company_exist = check_query_data.check_signle_column(c1='company_name',d1=company_name)
    email_exist = check_query_data.check_signle_column(c1='email',d1=email)

    company_msg = "Company already exist"
    email_msg = "Email already exists"
    
    #checks empty field and validates company_name and email
    if(len(name)==0 or len(company_name)==0 or len(email)==0 or len(password)==0):
        return render_template("register.html",field_empty="Please enter all fields")
    elif(company_exist and email_exist):
        return render_template("register.html",company_msg=company_msg,email_msg=email_msg)
    elif(company_exist):
        return render_template("register.html",company_msg=company_msg)
    elif(email_exist):
        return render_template("register.html",email_msg=email_msg)

    #inserts user data into db user table
    insert_data_database.insert_user_table(name,email,password,company_name)
    return render_template("dashboard.html")

#verify email page for forgot password
@app.route('/verify_email_initial')
def verify_email_initial():
    return render_template('for_email_verify.html')

#checks email(account) exists or not
@app.route('/verify_email',methods=['POST','GET'])
def verify_email():
    email=request.form.get('email'.lower())
    email_exist = check_query_data.check_signle_column('email',email)
    
    #puts data into session
    session["email"] = email

    if (email_exist):
        send_mail.mail(email)
        return('for_email_verify.html')
    return render_template('for_email_verify.html',field_empty='We cannot find your email')

#updates new password into db
@app.route('/forgot_password_verify',methods=['POST','GET'])
def forgot_password_verify():
    email = session.get("email")
    new_password=request.form.get('password')
    cnf_password=request.form.get('cnf_password')

    
    if(new_password == None and cnf_password == None):
        return render_template('forgot_password.html')
    elif(new_password==cnf_password):
        update_data_database.update_singel_data(cnf_password,email)
        return render_template('login.html')
    else:
        return render_template('forgot_password.html',invalid_msg='New password and confirm new password do not match')


if __name__ == "__main__":
    #secret_key for session
    app.secret_key='asdfghjkl'
    app.config['SESSION_TYPE'] ='filesystem'
    Session().init_app(app)
    app.run(debug=True)