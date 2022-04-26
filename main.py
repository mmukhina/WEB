from flask import Flask, url_for, request, render_template, redirect, send_from_directory
import json
import psycopg2
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, EqualTo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(message="Введите логин")])
    password = PasswordField('Пароль', validators=[DataRequired(message="Введите пароль")])
    submit = SubmitField('Войти')


def my_check(form, field):
    database_list = database("register")
    if field.data in database_list:
        raise ValidationError("Этот логин уже занят!")

def my_check_profile(form, field):
    database_list = [str(i) for i in database("available")]
    if (field.data not in database_list) or (int(field.data) == 1):
        raise ValidationError("Такой ID не существует!")
    
class RegisterForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(message="Введите логин"), my_check])
    password = PasswordField('Пароль', validators=[DataRequired(message="Введите пароль")])
    password_rep = PasswordField('Пароль', validators=[DataRequired(message="Введите пароль"),EqualTo('password', message='Пароли не совпадают')])
    checkbox = BooleanField("Я соглашаюсь на обработку персональных данных", validators=[DataRequired(message="Необходимое поле")])
    submit = SubmitField('Войти')


class Search(FlaskForm):
    username = StringField('ID: ', validators=[DataRequired(message="Введите id"), my_check_profile])
    submit = SubmitField('Создать игру')


    


black = {"A1":"", "A2": "", "A3": "", "A4": "", "A5": "", "A6": "", "A7": "pawnb", "A8": "rookb",
         "B1":"", "B2": "", "B3": "", "B4": "", "B5": "", "B6": "", "B7": "pawnb", "B8": "knightb",
         "C1":"", "C2": "", "C3": "", "C4": "", "C5": "", "C6": "", "C7": "pawnb", "C8": "bishopb",
         "D1":"", "D2": "", "D3": "", "D4": "", "D5": "", "D6": "", "D7": "pawnb", "D8": "queenb",
         "E1":"", "E2": "", "E3": "", "E4": "", "E5": "", "E6": "", "E7": "pawnb", "E8": "kingb",
         "F1":"", "F2": "", "F3": "", "F4": "", "F5": "", "F6": "", "F7": "pawnb", "F8": "bishopb",
         "G1":"", "G2": "", "G3": "", "G4": "", "G5": "", "G6": "", "G7": "pawnb", "G8": "knightb",
         "H1":"", "H2": "", "H3": "", "H4": "", "H5": "", "H6": "", "H7": "pawnb", "H8": "rookb"}

white = {"A1":"rookw", "A2": "pawnw", "A3": "", "A4": "", "A5": "", "A6": "", "A7": "", "A8": "",
         "B1":"knightw", "B2": "pawnw", "B3": "", "B4": "", "B5": "", "B6": "", "B7": "", "B8": "",
         "C1":"bishopw", "C2": "pawnw", "C3": "", "C4": "", "C5": "", "C6": "", "C7": "", "C8": "",
         "D1":"queenw", "D2": "pawnw", "D3": "", "D4": "", "D5": "", "D6": "", "D7": "", "D8": "",
         "E1":"kingw", "E2": "pawnw", "E3": "", "E4": "", "E5": "", "E6": "", "E7": "", "E8": "",
         "F1":"bishopw", "F2": "pawnw", "F3": "", "F4": "", "F5": "", "F6": "", "F7": "", "F8": "",
         "G1":"knightw", "G2": "pawnw", "G3": "", "G4": "", "G5": "", "G6": "", "G7": "", "G8": "",
         "H1":"rookw", "H2": "pawnw", "H3": "", "H4": "", "H5": "", "H6": "", "H7": "", "H8": ""}


def database(state, info=None):
    DATABASE_URL = "postgres://qybkrxdzbfsmnq:4abdee2cf19e5e24290e8b6f813fa91c9fded73e4ac639b3994bd3acf2f77bdb@ec2-3-209-61-239.compute-1.amazonaws.com:5432/dbu1marqhos8n6"

    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = conn.cursor()
    except Exception:
        state = "error"

    if state == "register":
        cur.execute("SELECT name FROM users")
        temp = cur.fetchall()
        result = [i[0] for i in temp]
        
    elif state == "login":
        cur.execute("SELECT name, password FROM users WHERE name = '{}';".format(info[0]))
        result = cur.fetchall()
        if result == []:
            return "error"

    elif state == "insert": 
        cur.execute("INSERT INTO users(name, password, picture) VALUES ('{}', '{}', 'dafault.png')".format(info[0], info[1]))
        conn.commit()

        cur.execute("SELECT id FROM users WHERE name = '{}';".format(info[0]))
        id_user = cur.fetchall()[0][0]
        
        cur.execute("INSERT INTO statistic (user_id) VALUES ({})".format(id_user))
        conn.commit()
        result = "success"

    elif state == "profile":
        cur.execute("SELECT id FROM users WHERE name = '{}';".format(info[0]))
        result = cur.fetchall()[0][0]

    elif state == "profile_data":
        cur.execute("SELECT win, lose, draw FROM statistic WHERE user_id = '{}';".format(info[0]))
        result = cur.fetchall()[0]

    elif state == "available":
        cur.execute("SELECT id FROM users")
        temp = cur.fetchall()
        result = [i[0] for i in temp]

    elif state == "admin":
        cur.execute("SELECT (id, name) FROM users WHERE id != 1")
        result = [i[0].replace("(", "").replace(")", "").split(",") for i in cur.fetchall()]

        cur.execute("SELECT (win, lose, draw) FROM statistic")
        result2 = [i[0].replace("(", "").replace(")", "").split(",") for i in cur.fetchall()]

        return [i + result2[ind] for ind, i in enumerate(result)]
        
    elif state == "error":
        return "no_in"

        
    cur.close()

    conn.close()

    return result
    
    


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = request.form['username']
        password = request.form['password']
        state = "login"
        
        check = database(state, [username])
        if check == "no_in":
            form.password.errors.append("Проверьте подключение к интернетy")
        elif check != "error" and check[0][1] == password:
            if username == "admin":
                return redirect(url_for('admin'))
            return redirect(url_for('profile', username=username))
        else:
            form.password.errors.append("Проверьте логин или пароль")

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = request.form['username']
        password = request.form['password']

        insert = database("insert", [username, password])
        
        if insert == "no_in":
            form.password.errors.append("Проверьте подключение к интернетy")
        elif insert == "success":
            return redirect(url_for('login'))

    return render_template('register.html', form=form)


class Game():
    def __init__(self):
        self.list_move = 0




@app.route('/main/<players>', methods=['GET', 'POST'])
def main(players):
    if request.method == 'POST':
        move = json.loads(request.data)
        if white[move] == "":
            white[move] = "pawnw"
            
    return render_template('main.html', black=black, white=white)

@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    form = Search()
    result_id = database("profile", [username])
    result_data = database("profile_data", [result_id])
    state = 1
        
    if request.method == 'POST':
        if form.validate_on_submit():
            apponent = request.form['username']
            if apponent == str(result_id):
                form.username.errors.append("Это ваш ID")
            else:
                return redirect(url_for('main', players=[result_id, int(apponent)]))

        else:
            return render_template('profile.html', win=result_data[0], lose=result_data[1], draw=result_data[2],
                               id_user=result_id, name_user=username, form=form, state=state)

    return render_template('profile.html', win=result_data[0], lose=result_data[1], draw=result_data[2],
                               id_user=result_id, name_user=username, form=form, state=state)

@app.route('/facts')
def facts():
    return render_template('facts.html')

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/admin')
def admin():
    user_info = database("admin")
    return render_template('admin.html', user_info=user_info)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
