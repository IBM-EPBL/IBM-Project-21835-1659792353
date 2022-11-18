import base64
import os
from flask import *
import ibm_db
import sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail



from flask_session import Session

con = ibm_db.connect("DATABASE=bludb; HOSTNAME=ba99a9e6-d59e-4883-8fc0-d6a8c9f7a08f.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud; PORT=31321; SECURITY=SSL; SSLServerCertificate=DigiCertGlobalRootCA.crt; UID=qxh83236; PWD=nNnU0FLB0HNnzAzZ",'','')

class fetch_query_data:
    def fetch_data(sql):
        list = []
        stmt = ibm_db.exec_immediate(con, sql)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            list.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
        if list:
            return list
        else:
            print("Data not fetched..............")

class check_query_data:

    def check_signle_column(t,c1,d1):
        sql = f"SELECT * FROM {t} WHERE {c1} ='{d1}';"
        return check_query_data.output(sql)
    
    def check_two_column(t,c1,d1,c2,d2):
        sql = f"SELECT * FROM {t} WHERE {c1} ='{d1}' AND {c2}='{d2}';"
        return check_query_data.output(sql)

    def output(sql):
        stmt = ibm_db.exec_immediate(con,sql)
        return ibm_db.fetch_tuple(stmt)



class insert_data_database:

    def insert_user_table(name,email,password,company_name):
        inser_sql = f"INSERT INTO user (name,email,password,company_name ) VALUES (?,?,?,?);"
        stmt = ibm_db.prepare(con, inser_sql)
        ibm_db.bind_param(stmt, 1, name)
        ibm_db.bind_param(stmt, 2, email)
        ibm_db.bind_param(stmt, 3, password)
        ibm_db.bind_param(stmt, 4, company_name)
        ibm_db.execute(stmt)

    def insert_item_table(supplier,product_name,purchase_price,selling_price,stock,email,status,low_stock):
        user_id=check_query_data.check_signle_column('user','email',email)
        sql = f"INSERT INTO product_details_{user_id[0]}(supplier,product_name,purchase_price,selling_price,stock,total_selling_price,status,low_stock)VALUES (?,?,?,?,?,?,?,?);"
        stmt = ibm_db.prepare(con, sql)
        ibm_db.bind_param(stmt, 1, supplier)
        ibm_db.bind_param(stmt, 2, product_name)
        ibm_db.bind_param(stmt, 3, purchase_price)
        ibm_db.bind_param(stmt, 4, selling_price)
        ibm_db.bind_param(stmt, 5, stock)
        t_selling_price = int(selling_price)*int(stock)
    
        ibm_db.bind_param(stmt, 6, t_selling_price)
        ibm_db.bind_param(stmt,7,status)
        ibm_db.bind_param(stmt,8,low_stock)
        ibm_db.execute(stmt)

    

class update_data_database:

    def update_singel_data(new_data,email):
        inser_sql = f"UPDATE user SET password='{new_data}' WHERE email='{email}';"
        ibm_db.exec_immediate(con, inser_sql)
    

        
    def sale(admin_email,customer_name,customer_email,phone_number,product_id,quantity,user_id):
        data = check_query_data.check_signle_column(f'product_details_{user_id[0]}','product_id',product_id)
        product_id = data[0]
        product_name = data[3]
        purchase_price = data[4]
        selling_price= data[5]
        stock = data[6]
        total_selling_price = data[7]
        low_stock_limit = data[9]
        billing_amount = selling_price*quantity
        total_selling_price -= billing_amount
        
        if(quantity<=stock):
            stock -= quantity
            sql = f"INSERT INTO sales_details_{user_id[0]}(customer_name,customer_email,product_id,phone_number,product_name,quantity,billing_amount)VALUES (?,?,?,?,?,?,?);"
            stmt = ibm_db.prepare(con, sql)
            ibm_db.bind_param(stmt, 1, customer_name)
            ibm_db.bind_param(stmt, 2, customer_email)
            ibm_db.bind_param(stmt, 3, product_id)
            ibm_db.bind_param(stmt, 4, phone_number)
            ibm_db.bind_param(stmt, 5, product_name)
            ibm_db.bind_param(stmt, 6, quantity)
            ibm_db.bind_param(stmt, 7, billing_amount)
            ibm_db.execute(stmt)

            if (stock > low_stock_limit):
                status = 'Instock'
            elif (stock <= low_stock_limit and stock > 1):
                status = 'Low stock'
                send_mail.mail_low_stock(admin_email,product_name,stock,low_stock_limit)
            elif (stock == 0):
                status = 'out of stock'
                send_mail.mail_out_of_stock(admin_email,product_name)

            updata_items =f"UPDATE product_details_{user_id[0]} SET total_selling_price= {total_selling_price}, stock = {stock}, status = '{status}' WHERE product_id={product_id}"
            ibm_db.exec_immediate(con, updata_items)
            existing_profit = user_id[5]
            if existing_profit == None:
                existing_profit = 0
            profit = (int(existing_profit)+((selling_price*quantity)-(purchase_price*quantity)))
            profit_sql = f"UPDATE user SET profit = {profit} where user_id ={user_id[0]}"
            ibm_db.exec_immediate(con, profit_sql)

            return 1
        else:
            return stock
            
    
    



class create_table:
    def item_table(email):
        user_id=check_query_data.check_signle_column('user','email',email)
        sql=f"CREATE TABLE product_details_{user_id[0]}(product_id BIGINT NOT NULL GENERATED ALWAYS AS IDENTITY (START WITH 1, INCREMENT BY 1),supplier VARCHAR(50),date timestamp DEFAULT CURRENT_TIMESTAMP,product_name VARCHAR(50) NOT NULL UNIQUE,purchase_price BIGINT,selling_price BIGINT,stock BIGINT,total_selling_price BIGINT,status VARCHAR(20),low_stock BIGINT,PRIMARY KEY (product_id));"
        ibm_db.exec_immediate(con, sql)

    def sales_table(admin_email):
        user_id=check_query_data.check_signle_column('user','email',admin_email)
        sql = f"CREATE TABLE sales_details_{user_id[0]}(sales_id BIGINT NOT NULL GENERATED ALWAYS AS IDENTITY (START WITH 1, INCREMENT BY 1),customer_name VARCHAR(50),customer_email VARCHAR(50),product_id BIGINT,phone_number BIGINT,date timestamp DEFAULT CURRENT_TIMESTAMP,product_name VARCHAR(50),quantity BIGINT,billing_amount BIGINT,PRIMARY KEY (sales_id));"
        ibm_db.exec_immediate(con, sql)

    def low_stock(admin_email):
        user_id=check_query_data.check_signle_column('user','email',admin_email)
        sql = f"CREATE TABLE low_stock_{user_id[0]}"


class send_mail:
    
    def mail(email):
        encoded_email = code.encode(email)
        encoded_email = f"{encoded_email}"
        encoded_email= encoded_email[2:len(encoded_email)-1]
        message = Mail(from_email='inventorymanagementvsgp@gmail.com',
            to_emails=email,
            subject='Reset password',  
            html_content='<h3>Hello!, <br>A request has been received to change the password for your Inventory account</h3><a href="http://127.0.0.1:5000/forgot_password_verify/{}"><button type="submit" style="background-color: #0583d2; border: none; color: white; padding: 12px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; border-radius: 5px">Reset Password</button>'.format(encoded_email))
        sg = SendGridAPIClient("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")
        response = sg.send(message)
        print(response.status_code, response.body)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    def mail_low_stock(email,product_name,stock,limit):
        encoded_email = code.encode(email)
        encoded_email = f"{encoded_email}"
        encoded_email= encoded_email[2:len(encoded_email)-1]
        message = Mail(from_email='inventorymanagementvsgp@gmail.com',
            to_emails=email,
            subject='Low stock alert mail',  
            html_content='<h3>Hello!, <br> You recieved this alert because product- {} current stock is {} lower than the threashold you have set.</h3><a href="http://127.0.0.1:5000"><button type="submit" style="background-color: #0583d2; border: none; color: white; padding: 12px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; border-radius: 5px">Login</button>'.format(product_name,stock,limit))
        sg = SendGridAPIClient("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")
        response = sg.send(message)
        print(response.status_code, response.body)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    def mail_out_of_stock(email,product_name):
        encoded_email = code.encode(email)
        encoded_email = f"{encoded_email}"
        encoded_email= encoded_email[2:len(encoded_email)-1]
        message = Mail(from_email='inventorymanagementvsgp@gmail.com',
            to_emails=email,
            subject='Product out of stock',  
            html_content='<h3>Hello!, <br> You recieved this alert because product :{} is out of stock now.</h3><a href="http://127.0.0.1:5000"><button type="submit" style="background-color: #0583d2; border: none; color: white; padding: 12px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; border-radius: 5px">Login</button>'.format(product_name))
        sg = SendGridAPIClient("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")
        response = sg.send(message)
        print(response.status_code, response.body)
        print(response.status_code)
        print(response.body)
        print(response.headers)



class code:
    def encode(data):
        encode = data.encode("utf-8")
        return base64.b16encode(encode)

    def decode(data):
        return base64.b16decode(data).decode("utf-8")


class check:
    def check(email):
        user_id=check_query_data.check_signle_column('user','email',email)
        return check_query_data.output(f"SELECT count(product_id) FROM product_details_{user_id[0]}")




class dashboard_view:
    def total_items(email):
        count = check.check(email)
        return count[0]
    
    def dashboard_profit(email):
        sql = f"SELECT profit FROM user WHERE email = '{email}'"
        stmt = ibm_db.exec_immediate(con,sql)
        data = ibm_db.fetch_tuple(stmt)
        temp = 0
        if data[0] == None:
            return temp
        return data[0]
        

    def low_stock(email):
            user_id = check_query_data.check_signle_column('user','email',email)
            sql = f"SELECT count(product_id) FROM product_details_{user_id[0]} WHERE stock <= 10"
            stmt = ibm_db.exec_immediate(con,sql)
            data = ibm_db.fetch_tuple(stmt)
            return data[0]

    def stock_cost(email):
            user_id = check_query_data.check_signle_column('user','email',email)
            print(user_id)
            sql = f"SELECT sum(total_selling_price) FROM product_details_{user_id[0]}"
            stmt = ibm_db.exec_immediate(con,sql)
            data = ibm_db.fetch_tuple(stmt)
            temp = 0
            if data[0] == None:
                return temp
            return data[0]

    def dashboard_details(email):
        total_item = dashboard_view.total_items(email)
        profit = dashboard_view.dashboard_profit(email)
        low_stock = dashboard_view.low_stock(email)
        stock_cost = dashboard_view.stock_cost(email)
        return render_template('dashboard.html',total_item=total_item,profit=profit,low_stock=low_stock,stock_cost=stock_cost)
