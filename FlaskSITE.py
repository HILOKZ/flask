import os
import sqlite3

from flask import Flask, render_template, g, request, flash, abort, redirect, url_for
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from FDataBase import FDataBase
from UserLogin import UserLogin

DATABASE = '/tmp/flasksite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'

app = Flask(__name__)
app.config.from_object(__name__)

login_manager = LoginManager(app)
login_manager.login_view = 'register'
login_manager.login_message = 'Авторизуйтесь или зарегистрируйтесь чтобы добавить или прочитать статью'


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)


app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flasksite.db')))


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


dbase = None


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/")
def index():
    return render_template('index.html', title='Главная')


@app.route('/newspost')
def newspost():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('newspost.html', title='Статьи', posts=dbase.getPostsAnonce())


@app.route("/newspost/<int:id_post>")
@login_required
def showPost(id_post):
    title, post = dbase.getPost(id_post)
    if not title:
        abort(404)

    return render_template('post.html', title=title, post=post)


@app.route("/add_article", methods=["POST", "GET"])
@login_required
def addPost():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 3:
            res = dbase.addPost(request.form['name'], request.form['post'])
            if not res:
                flash('Ошибка добавления статьи')
            else:
                flash('Статья добавлена успешно')
                return redirect(url_for('newspost'))
        else:
            flash('Ошибка добавления статьи')

    return render_template('add_article.html', title='Добавить статью')


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['password'], request.form['password']):
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            return redirect(url_for('newspost'))

        flash("Неверная пара логин/пароль")

    return render_template("login.html", title="Авторизация")


@app.route("/registration", methods=["POST", "GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == "POST":
        if len(request.form['username']) > 4 and len(request.form['email']) > 4 \
                and len(request.form['password']) > 4 and request.form['password'] == request.form['rpassword']:
            hash = generate_password_hash(request.form['password'])
            res = dbase.addUser(request.form['username'], request.form['email'], hash)
            if res:
                flash("Регистрация успешна!")
                return redirect('login')
            else:
                flash("Ошибка! Проверьте данные")
        else:
            flash("Неверно заполнены данные")

    return render_template("registration.html", title="Регистрация")


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', enter=current_user.get_id())


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
