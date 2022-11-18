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
    email = session.get("email")
    total_item = dashboard_view.total_items(email)
    profit = dashboard_view.dashboard_profit(email)
    low_stock = dashboard_view.low_stock(email)
    stock_cost = dashboard_view.stock_cost(email)
    user_id=check_query_data.check_signle_column('user','email',email)
    data = fetch_query_data.fetch_data(f"SELECT * FROM product_details_{user_id[0]} WHERE stock <=10 ")
    if data:
        
        return render_template('dashboard.html',total_item=total_item,profit=profit,low_stock=low_stock,stock_cost=stock_cost,users=data)
    return render_template('dashboard.html',total_item=total_item,profit=profit,low_stock=low_stock,stock_cost=stock_cost)

#login_validator
@app.route('/login_validation',methods=['GET','POST'])
def login_validation():
    email=request.form.get('email').lower()
    password=request.form.get('password')
    session["email"] = email
    print(f'{email}-----------------------------------------------------------------------------------------------------------')
    
    #checking for email and password in db
    if (check_query_data.check_two_column(t='user',c1='email',d1=email,c2='password',d2=password)):
        email = session.get("email")
        total_item = dashboard_view.total_items(email)
        profit = dashboard_view.dashboard_profit(email)
        low_stock = dashboard_view.low_stock(email)
        stock_cost = dashboard_view.stock_cost(email)
        return render_template('dashboard.html',total_item=total_item,profit=profit,low_stock=low_stock,stock_cost=stock_cost)
    else:
        return render_template('login.html',invalid_msg='Invalid login credentials')

#register_validator
@app.route('/register_validation',methods=['GET','POST'])
def register_validation():
    
    name=request.form.get('name')
    company_name=request.form.get('company').lower()
    email=request.form.get('email').lower()
    password=request.form.get('password')
    session["email"] = email
    #checks already email and company_name exist in db
    company_exist = check_query_data.check_signle_column(t='user',c1='company_name',d1=company_name)
    email_exist = check_query_data.check_signle_column(t='user',c1='email',d1=email)

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
    create_table.item_table(email)
    create_table.sales_table(email)
    return render_template("dashboard.html")

#checks email(account) exists or not
@app.route('/verify_email',methods=['POST','GET'])
def verify_email():
    if request.method == 'POST':
        email=request.form.get('email')
        email_exist = check_query_data.check_signle_column('user','email',email)
        
        #puts data into session
        session["email"] = email 

        if (email_exist):
            send_mail.mail(email)
            return render_template('for_email_verify.html',field_empty='We have e-mailed your password reset link!')
        return render_template('for_email_verify.html',field_empty='We cannot find your email')
    
    return render_template('for_email_verify.html')


#forgot password
@app.route('/forgot_password_verify/<email>',methods=['POST','GET'])
def forgot_password_verify(email):
    if request.method == 'POST':
        decode_email = session.get("decode_email").lower()
        new_password=request.form.get('password')
        cnf_password=request.form.get('cnf_password')
        if(len(new_password) == 0 and len(cnf_password) == 0):
            return render_template('forgot_password.html',invalid_msg='Please enter password')
        elif(new_password==cnf_password):
            update_data_database.update_singel_data(cnf_password,decode_email)
            return render_template('login.html')
        else:
            return render_template('forgot_password.html',invalid_msg='New password and confirm new password do not match')

    decode_email = code.decode(f"{email}")
    session["decode_email"] = decode_email
    return render_template("forgot_password.html")


@app.route('/items',methods=['POST','GET'])
def items():
    email = session.get("email")
    user_id=check_query_data.check_signle_column('user','email',email)
    data = fetch_query_data.fetch_data(f"SELECT * FROM product_details_{user_id[0]}")
    if data:
        
        return render_template("items.html",users=data)
    return render_template("items.html",empty="Once item is purchase it will be shown here")

@app.route('/purchase_order',methods=['POST','GET'])
def purchase():

    if request.method == 'POST':
        email = session.get("email")
        product_name=request.form.get('product_name').lower()
        supplier_name=request.form.get('Supplier_name')
        purchase_price=request.form.get('purchase_price')
        selling_price=request.form.get('selling_price')
        quantity=request.form.get('quantity')
        low_stock=request.form.get('low_stock')
        status='Instock'
        if (email=="" or product_name=="" or supplier_name=="" or selling_price=="" or quantity=="" or status==""):
             return render_template("purchase_order.html",invalid_msg="Please Fill all details")

        user_id = check_query_data.check_signle_column('user','email',email)
        data = check_query_data.check_signle_column(f'product_details_{user_id[0]}','product_name',product_name)
        if data:
            return render_template("purchase_order.html",invalid_msg="Product name already exist")
        print(f'{status}3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333')
        insert_data_database.insert_item_table(supplier_name,product_name,purchase_price,selling_price,quantity,email,status,low_stock)
        return render_template("purchase_order.html",msg="Item added to purchase list")
    return render_template("purchase_order.html")

@app.route("/sales",methods=['POST','GET'])
def sales():
    if request.method == 'POST':
        admin_email = session.get("email")
        customer_name=request.form.get('customer_name')
        customer_email=request.form.get('customer_email')
        phone_number=request.form.get('phone_number')
        product_id=request.form.get('product_id')
        quantity=request.form.get('quantity')
        print(f"{product_id}----------------------------------------------------------------------------------------------")
        if (product_id=="" or customer_email== "" or customer_name == "" or phone_number=="" or quantity=="" ):
            return render_template("sales_page.html",error = "Plese fill all details")
        user_id = check_query_data.check_signle_column('user','email',admin_email)
        print(f"{user_id}----------------------------------------------------------------------------------------------")

        sql = f"SELECT * FROM product_details_{user_id[0]} where product_id = {product_id}"
        stmt = ibm_db.exec_immediate(con,sql)
        data = ibm_db.fetch_tuple(stmt)
        if data==False:
            return render_template("sales_page.html",invalid_msg="Product doesn't exist")
        status = data[8]
        if status  == 'out of stock':
            return render_template("sales_page.html",msg="Product")
        
        update = update_data_database.sale(admin_email,customer_name,customer_email,int(phone_number),product_id,int(quantity),user_id)
        if update == 1:
            return render_template("sales_page.html",msg="Item Sold")
        else:
            return render_template("sales_page.html",msg=f"Low stock only {update} item left")
    return render_template("sales_page.html")

@app.route('/delete/<name>')
def delete(name):
  #sql = f"SELECT * FROM Students WHERE name='{escape(name)}'"
  #print(sql)
  #stmt = ibm_db.exec_immediate(conn, sql)
  #student = ibm_db.fetch_row(stmt)
  #print ("The Name is : ",  student)
  #if student:
    email = session.get("email")
    user_id = check_query_data.check_signle_column('user','email',email)
    print(user_id)
    sql = f"DELETE FROM product_details_{user_id[0]} WHERE product_id='{escape(name)}'"
    print(sql)
    stmt = ibm_db.exec_immediate(con, sql)
    data = fetch_query_data.fetch_data(f"SELECT * FROM product_details_{user_id[0]}")
    if data:
        
        return render_template("items.html",users=data)
    return render_template("items.html",empty="Once item is purchase it will be shown here")


if __name__ == "__main__":
    #secret_key for session
    app.secret_key='asdfghjkl'
    app.config['SESSION_TYPE'] ='filesystem'
    Session().init_app(app)
    app.run(debug=True)