from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', title = 'Главная')

@app.route('/registration')
def registration():
    return render_template('registration.html', title = 'Регистрация')

@app.route('/news')
def news():
    return render_template('news.html', title = 'Статьи')

@app.route('/login')
def login():
    return render_template('login.html', title = 'Войти')

if __name__ == '__main__':
    app.debug = True
    app.run()
