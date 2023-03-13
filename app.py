from flask import Flask,render_template,request,redirect,url_for,session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pandas as pd
app = Flask(__name__)


app.secret_key = "xyzsdfg"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ta_allocation'

mysql = MySQL(app)



@app.route("/")
@app.route("/login",methods = ['GET','POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM LOGIN WHERE email = % s AND password = % s',(email,password,))

        user = cursor.fetchone()

        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']

            mesage = 'Logged in successfully !'
            cursor.close()
            return render_template('user.html',mesage = mesage)
        
        else:
            mesage = 'Please enter valid credentials !'

    return render_template('login.html',mesage= mesage)


@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('userid',None)
    session.pop('email',None)
    return redirect(url_for('login'))



@app.route('/register',methods = ['GET','POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'userid' in request.form and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userid = request.form['userid']
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM login WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userid or not name or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO login VALUES (% s, % s, % s, % s)', (userid,name, email, password, ))
            mysql.connection.commit()
            cursor.close()
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    
    
    return render_template('register.html', mesage = mesage)



@app.route('/view',methods = ['GET','POST'])
def view():
    mesage = ''
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('TRUNCATE TABLE ta_table')
    mysql.connection.commit()
    file = request.files['file']
    file.save(file.filename)

    data = pd.read_excel(file)
    
    # data = data.shape[0]

    for index_ in range(data.shape[0]):
        sid = data["reg"][index_]
        name = data["name"][index_]

        cursor.execute('INSERT INTO ta_table VALUES (% s, % s)', (sid,name, ))
        mysql.connection.commit()
        cursor.close()
    return render_template('user.html',table = data) 



@app.route('/show',methods = ['GET','POST'])
def show():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM ta_table')
    table = cursor.fetchall()
    cursor.close()
    return render_template('table.html',table=table)


@app.route('/update' , methods = ['GET','POST'])
def update():
    if request.method == 'POST':
        sid = request.form['sid']
        name = request.form['name']

        cursor = mysql.connection.cursor()
        cursor.execute("""
        
        UPDATE ta_table 
        SET name= %s  
        WHERE sid = %s      
        
        """,(name,sid))


        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('show'))


@app.route('/delete/<string:id_data>', methods = ['POST','GET'])
def delete(id_data):
    cursor = mysql.connection.cursor()

    cursor.execute("DELETE from ta_table WHERE sid=%s",[id_data])
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('show'))



if __name__ == "__main__":
    app.run(debug=True)