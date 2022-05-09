from flask import Flask, url_for, request, render_template,redirect, send_from_directory, make_response, flash
import json
import psycopg2
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, EqualTo
from flask_socketio import SocketIO, send, emit
from werkzeug.utils import secure_filename
import urllib.request
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)
DATABASE_URL = os.environ['DATABASE_URL']

black_orig = {"A1":"", "A2": "", "A3": "", "A4": "", "A5": "", "A6": "", "A7": "pawnb", "A8": "rookb",
         "B1":"", "B2": "", "B3": "", "B4": "", "B5": "", "B6": "", "B7": "pawnb", "B8": "knightb",
         "C1":"", "C2": "", "C3": "", "C4": "", "C5": "", "C6": "", "C7": "pawnb", "C8": "bishopb",
         "D1":"", "D2": "", "D3": "", "D4": "", "D5": "", "D6": "", "D7": "pawnb", "D8": "queenb",
         "E1":"", "E2": "", "E3": "", "E4": "", "E5": "", "E6": "", "E7": "pawnb", "E8": "kingb",
         "F1":"", "F2": "", "F3": "", "F4": "", "F5": "", "F6": "", "F7": "pawnb", "F8": "bishopb",
         "G1":"", "G2": "", "G3": "", "G4": "", "G5": "", "G6": "", "G7": "pawnb", "G8": "knightb",
         "H1":"", "H2": "", "H3": "", "H4": "", "H5": "", "H6": "", "H7": "pawnb", "H8": "rookb"}

white_orig = {"A1":"rookw", "A2": "pawnw", "A3": "", "A4": "", "A5": "", "A6": "", "A7": "", "A8": "",
         "B1":"knightw", "B2": "pawnw", "B3": "", "B4": "", "B5": "", "B6": "", "B7": "", "B8": "",
         "C1":"bishopw", "C2": "pawnw", "C3": "", "C4": "", "C5": "", "C6": "", "C7": "", "C8": "",
         "D1":"queenw", "D2": "pawnw", "D3": "", "D4": "", "D5": "", "D6": "", "D7": "", "D8": "",
         "E1":"kingw", "E2": "pawnw", "E3": "", "E4": "", "E5": "", "E6": "", "E7": "", "E8": "",
         "F1":"bishopw", "F2": "pawnw", "F3": "", "F4": "", "F5": "", "F6": "", "F7": "", "F8": "",
         "G1":"knightw", "G2": "pawnw", "G3": "", "G4": "", "G5": "", "G6": "", "G7": "", "G8": "",
         "H1":"rookw", "H2": "pawnw", "H3": "", "H4": "", "H5": "", "H6": "", "H7": "", "H8": ""}


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
    password_rep = PasswordField('Повторите пароль', validators=[DataRequired(message="Введите пароль"),EqualTo('password', message='Пароли не совпадают')])
    checkbox = BooleanField("Я соглашаюсь на обработку персональных данных", validators=[DataRequired(message="Необходимое поле")])
    submit = SubmitField('Войти')


class Search(FlaskForm):
    username = StringField('ID: ', validators=[DataRequired(message="Введите id"), my_check_profile])
    submit = SubmitField('Создать игру')
    

class Game(FlaskForm):
    end_game = SubmitField("Закончить игру")
    win = SubmitField("Мат")
    draw = SubmitField("Пат")
    

def database(state, info=None):
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
            result = "error"
        else:
            cur.execute("UPDATE users SET picture = 'default.png' WHERE name = '{}'".format(info[0]))
            conn.commit()

    elif state == "insert": 
        cur.execute("INSERT INTO users(name, password, picture) VALUES ('{}', '{}', 'default.png')".format(info[0], info[1]))
        conn.commit()

        cur.execute("SELECT id FROM users WHERE name = '{}';".format(info[0]))
        id_user = cur.fetchall()[0][0]
        
        cur.execute("INSERT INTO statistic (user_id) VALUES ({})".format(id_user))
        conn.commit()
        result = "success"

    elif state == "profile":
        cur.execute("SELECT id, picture FROM users WHERE name = '{}';".format(info[0]))
        result = cur.fetchall()[0]

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

        result = [i + result2[ind] for ind, i in enumerate(result)]

    elif state == "room":
        cur.execute("SELECT * FROM game")
        try:
            result = cur.fetchall()[0]
        except Exception:
            result = []

    elif state == "create_room":
        cur.execute("INSERT INTO game (player, apponent) VALUES ({}, {})".format(info[0], info[1]))
        conn.commit()
        result = "success"

    elif state == "close":
        try:
            cur.execute("DELETE FROM game")
            cur.execute("DELETE FROM moves")
            conn.commit()
            result = "success"
        except Exception:
            result = "closed"

    elif state == "add_win_lose":
        cur.execute("UPDATE statistic SET win = win + 1 WHERE user_id = '{}'".format(int(info[0])))
        cur.execute("UPDATE statistic SET lose = lose + 1 WHERE user_id = '{}'".format(int(info[1])))
        conn.commit()
        result = "success"

    elif state == "add_draw":
        cur.execute("UPDATE statistic SET draw = draw + 1 WHERE user_id = '{}'".format(int(info[0])))
        cur.execute("UPDATE statistic SET draw = draw + 1 WHERE user_id = '{}'".format(int(info[1])))
        conn.commit()
        result = "success"

    elif state == "change_pic":
        cur.execute("UPDATE users SET picture = '{}' WHERE name = '{}'".format(info[1], info[0]))
        conn.commit()
        result = "success"

    elif state == "add":
        cur.execute("INSERT INTO moves (move) VALUES ('{}')".format(info[0]))
        conn.commit()
        result = "success"

    elif state == "moves":
        cur.execute("SELECT * FROM moves")
        temp = cur.fetchall()
        result = [i[0] for i in temp]
        
    elif state == "error":
        result = "no_in"

        
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





@app.route('/main/<info>', methods=['GET', 'POST'])
def main(info):
    form = Game()
    info = info.split(" ")
    moves = database("moves")
    black_lis = ["kingb", "queenb", "pawnb", "bishopb", "rookb", "knightb"]
    white_lis = ["kingw", "queenw", "pawnw", "bishopw", "rookw", "knightw"]

    black = black_orig.copy()
    white = white_orig.copy()
                                
    for i in moves:
        temp = i.split(" ")
        if temp[0] == "d":
            try:
                white[temp[1]] = ""
                black[temp[1]] = ""
            except Exception:
                pass
        elif temp[0] == "p":
            if len(temp) == 3:
                if temp[2] in black_lis:
                    try:
                        black[temp[1]] = temp[2]
                    except Exception:
                        pass
                elif temp[2] in white_lis:
                    try:
                        white[temp[1]] = temp[2]
                    except Exception:
                        pass
                    
                
    if request.method == 'POST':
        if form.end_game.data:
            close = database("close")
            return redirect(url_for('profile', username=info[2]))
        elif form.win.data:
            close = database("close")
            if close != "closed":
                add_win_lose = database("add_win_lose", info)
            return redirect(url_for('profile', username=info[2]))
        elif form.draw.data:
            close = database("close")
            if close != "closed":
                add_draw = database("add_draw", info)
            return redirect(url_for('profile', username=info[2]))
        
            
    return render_template('main.html', black=black, white=white, player=info[0], apponent=info[1], form=form, moves=moves)


@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    form = Search()
    result = database("profile", [username])
    result_id = result[0]
    image = result[1]
    result_data = database("profile_data", [result_id])
    room = database("room")

    if room == []:
        state = 0
        apponent = 0
    elif result_id == room[0]:
        state = 1
        apponent = room[1]
    elif result_id == room[1]:
        state = 1
        apponent = room[0]
        
        
    if request.method == 'POST':
        if form.validate_on_submit():
            apponent = request.form['username']
            if apponent == str(result_id):
                form.username.errors.append("Это ваш ID")
            elif room == []:
                create_room = database("create_room", [result_id, int(apponent)])
                return redirect(url_for('main', info=str(result_id) + " " + apponent + " " + username))
            else:
                form.username.errors.append("Подождите пока закончиться игра")

        else:
            return render_template('profile.html', win=result_data[0], lose=result_data[1], draw=result_data[2],
                               id_user=result_id, name_user=username, form=form, state=state, apponent=apponent, image=image)

    return render_template('profile.html', win=result_data[0], lose=result_data[1], draw=result_data[2],
                               id_user=result_id, name_user=username, form=form, state=state, apponent=apponent, image=image)

@app.route('/facts/<username>')
def facts(username):
    return render_template('facts.html', username=username)

@app.route('/rules/<username>')
def rules(username):
    return render_template('rules.html', username=username)

@app.route('/admin')
def admin():
    user_info = database("admin")
    return render_template('admin.html', user_info=user_info)

@socketio.on("message")
def handleMessage(data):
    emit("new_message",data,broadcast=True)
    add = database("add", [data])


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
    

@app.route('/upload_form/<username>', methods=['GET', 'POST'])
def upload_form(username):
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('Нет файловой части')
                return render_template('upload.html', username=username)
            
            file = request.files['file']
            
            if file.filename == '':
                flash('Не выбрано изображение для загрузки')
                return render_template('upload.html', username=username)
                
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('Изображение успешно загружено и отображено ниже')
                change_pic = database("change_pic", [username, filename])
                return render_template('upload.html',username=username, filename=filename)
            else:
                flash('Допустимые типы изображений: png, jpg, jpeg')
                return render_template('upload.html', username=username)
        else:
                return render_template('upload.html', username=username)
    

@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


if __name__ == "__main__":
    #socketio.run(app, port=8080, host='127.0.0.1')
    socketio.run(app)
