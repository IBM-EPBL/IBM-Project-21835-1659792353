from flask import Flask,render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('Home.html')

@app.route("/login")
def login():
    return render_template('Login.html')

@app.route("/signup")
def signup():
    return render_template('Sign up.html')

@app.route("/about")
def about():
    return render_template('About.html')

if __name__ == '__main__':
    app.run(debug=True)