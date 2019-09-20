from flask import Flask, flash, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash
import pymysql
from tables import Results
from flaskext.mysql import MySQL
from wtforms import StringField, PasswordField, SubmitField, validators, Form
from passlib.hash import sha256_crypt
import sqlite3

app = Flask(__name__)
mysql = MySQL()
app.config.from_pyfile('vars.cfg')
mysql.init_app(app)

DATABASE = 'db.sqlite3'

user_list = {
    "user1": "password1",
    "user2": "password2"
}


@app.route('/', methods=['GET', 'POST'])
def main_page():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        db_select = f"SELECT password FROM admins WHERE username = '{username}'"
        cur = sqlite3.connect(DATABASE).cursor()
        answer = cur.execute(db_select)
        res = cur.fetchone()

        if res:
            password = res[0]
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid password'
                return render_template('login.html', error=error)
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


class RegisterForm(Form):
    username = StringField('Username', [validators.length(min=1, max=50)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    forma = RegisterForm(request.form)
    if request.method == 'POST' and forma.validate():
        username = forma.username.data
        password = sha256_crypt.encrypt(str(forma.password.data))
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        query = f"INSERT INTO admins(username, password) VALUES ('{username}', '{password}')"
        cur.execute(query)
        conn.commit()
        cur.close()
        flash("You are registered", 'success')
        return redirect((url_for('dashboard')))
    return render_template('register.html', form=forma)


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You are now logged out', 'logout')
    return redirect(url_for('main_page'))


@app.route('/new_user')
def add_user_view():
    return render_template('add.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/add', methods=['POST'])
def add_user():
    try:
        user_name = request.form['inputName']
        user_email = request.form['inputEmail']
        user_password = request.form['inputPassword']
        # validate the received values
        if user_name and user_email and user_password and request.method == 'POST':
            # do not save password as a plain text
            _hashed_password = generate_password_hash(_password)
            # save edits
            sql = "INSERT INTO users(user_name, user_email, user_password) VALUES(%s, %s, %s)"
            data = (user_name, user_email, _hashed_password,)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            flash('User added successfully!')
            return redirect('/')
        else:
            return 'Error while adding user'
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/list')
def users():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        table = Results(rows)
        table.border = True
        return render_template('users.html', table=table)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/edit/<int:id>')
def edit_view(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE user_id=%s", id)
        row = cursor.fetchone()
        if row:
            return render_template('edit.html', row=row)
        else:
            return 'Error loading #{id}'.format(id=id)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/update', methods=['POST'])
def update_user():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        _id = request.form['id']
        # validate the received values
        if _name and _email and _password and _id and request.method == 'POST':
            # do not save password as a plain text
            _hashed_password = generate_password_hash(_password)
            print(_hashed_password)
            # save edits
            sql = "UPDATE users SET user_name=%s, user_email=%s, user_password=%s WHERE user_id=%s"
            data = (_name, _email, _hashed_password, _id,)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            flash('User updated successfully!')
            return redirect('/')
        else:
            return 'Error while updating user'
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


@app.route('/delete/<int:id>')
def delete_user(id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id=%s", (id,))
        conn.commit()
        flash('User deleted successfully!')
        return redirect('/')
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run()
