from flask import Flask, flash, render_template, request, redirect
from flask_login import login_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
from tables import Results
from flaskext.mysql import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField


app = Flask(__name__)
app.config.from_pyfile('vars.cfg')

mysql = MySQL()

# MySQL configurations
app.config.from_pyfile('vars.cfg')


login_manager = LoginManager()
login_manager.init_app(app)

mysql.init_app(app)


class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')


@app.route('/', methods=['GET'])
def main_page():
    return render_template('login.html')


@app.route('/new_user')
def add_user_view():
    return render_template('add.html')


@app.route('/add', methods=['POST'])
def add_user():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
    # validate the received values
        if _name and _email and _password and request.method == 'POST':
            # do not save password as a plain text
            _hashed_password = generate_password_hash(_password)
            # save edits
            sql = "INSERT INTO tbl_user(user_name, user_email, user_password) VALUES(%s, %s, %s)"
            data = (_name, _email, _hashed_password,)
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
        cursor.execute("SELECT * FROM tbl_user")
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
        cursor.execute("SELECT * FROM tbl_user WHERE user_id=%s", id)
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
            sql = "UPDATE tbl_user SET user_name=%s, user_email=%s, user_password=%s WHERE user_id=%s"
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
        cursor.execute("DELETE FROM tbl_user WHERE user_id=%s", (id,))
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
