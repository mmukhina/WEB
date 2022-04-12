from flask import Flask, url_for, request, render_template
import json

app = Flask(__name__)

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    if request.method == 'GET':
            return render_template('register.html')
        
    elif request.method == 'POST':
        print(request.form['surname'])
        print(request.form['name'])
        print(request.form['email'])
        print(request.form['class'])
        print(request.form['file'])
        print(request.form['about'])
        print(request.form['sex'])
        print(request.form.get('prof1'))
        print(request.form.get('prof2'))
        print(request.form.get('prof3'))
        print(request.form.get('prof4'))
        print(request.form.get('prof5'))
        print(request.form.get('prof6'))
        print(request.form.get('prof7'))
        print(request.form.get('prof8'))
        print(request.form.get('accept'))
        return "redirect to login"

@app.route('/main')
def main():
    return render_template('main.html', black=black, white=white)


@app.route('/test', methods=['POST'])
def test():
    output = request.get_json()
    result = json.loads(output)
    print(result)
    return result


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
