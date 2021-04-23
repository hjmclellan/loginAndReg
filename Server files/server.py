from flask import Flask, render_template, request, redirect, session, flash
from mysqlconn import connectToMySQL
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

app = Flask(__name__)
from flask_bcrypt import Bcrypt        
bcrypt = Bcrypt(app)
app.secret_key = "This code is bananas; BaNaNaS"


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/create_user',methods=['POST'])
def create_user():
    if len(request.form['fname']) < 1:
        flash("***Please enter a first name***")
    if len(request.form['lname']) < 1:
        flash("***Please enter a last name***")
    if not EMAIL_REGEX.match(request.form['email']):
        flash("***Invalid email address***")
    if len(request.form['password']) < 8:
        flash("password must contain at least 8 characters")
    if request.form['cpassword'] != request.form['password']:
        flash("Passwords do not match")
    if not '_flashes' in session.keys():
        flash("Successfully registered!")
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(em)s, %(pass)s, NOW(), NOW());"
        data = {
            'fn': request.form['fname'],
            'ln': request.form['lname'],
            'em': request.form['email'],
            'pass': pw_hash,
        }
        mysql = connectToMySQL('loginandreg')
        user=mysql.query_db(query, data)
        session['user_id'] = user
        return redirect("/success")
    else:
        return redirect('/')

@app.route('/login_user',methods=['POST'])
def login_user():
    query = "SELECT * FROM users WHERE email = %(em)s;"
    data={
        'em': request.form['email']
    }
    mysql = connectToMySQL('loginandreg')
    result = mysql.query_db(query, data)
    if len(result) > 0:
        if bcrypt.check_password_hash(result[0]['password'], request.form['password']):
            session['user_id'] = result[0]['id']
            return redirect('/success')
    else:
        flash("You could not be logged in")
    return redirect('/')

@app.route('/success')
def success():
    return render_template("success.html")




if __name__=="__main__":
    app.run(debug=True)