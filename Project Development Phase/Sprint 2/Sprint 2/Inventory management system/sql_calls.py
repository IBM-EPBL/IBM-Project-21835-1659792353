import ibm_db
from app import *
import sendgrid
import os
from sendgrid.helpers.mail import *


con = ibm_db.connect("DATABASE=bludb; HOSTNAME=ba99a9e6-d59e-4883-8fc0-d6a8c9f7a08f.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud; PORT=31321; SECURITY=SSL; SSLServerCertificate=DigiCertGlobalRootCA.crt; UID=qxh83236; PWD=nNnU0FLB0HNnzAzZ",'','')


class check_query_data:

    def check_signle_column(c1,d1):
        sql = f"SELECT * FROM user WHERE {c1} ='{d1}';"
        return check_query_data.output(sql)
    
    def check_two_column(c1,d1,c2,d2):
        sql = f"SELECT * FROM user WHERE {c1} ='{d1}' AND {c2}='{d2}';"
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
        print("Data inserted")

class update_data_database:

    def update_singel_data(new_data,email):
        inser_sql = f"UPDATE user SET password='{new_data}' WHERE email='{email}';"
        ibm_db.exec_immediate(con, inser_sql)
        print("Data updated")


class send_mail:
    def mail(email):
        sg = sendgrid.SendGridAPIClient(api_key='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')
        from_email = Email("srijithramakrishnan01@gmail.com")
        to_email = To(email)
        subject = "Sending with SendGrid is Fun"
        html_content='<a href = http://127.0.0.1:5000/forgot_password_verify>Click </a>'
        mail = Mail(from_email, to_email, subject, html_content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)