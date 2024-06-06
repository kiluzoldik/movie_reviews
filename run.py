from flask import Flask, render_template, redirect, url_for
from app.database import Session
from app.models import User, Movie, Review
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

# Главная страница
@app.route('/')
def index():
    # Здесь можно получить данные для подборок фильмов из базы данных
    return render_template('index.html')

# Страница с информацией о фильме
@app.route('/movie/<int:movie_id>')
def movie(movie_id):
    session = Session()
    movie = session.query(Movie).get(movie_id)
    session.close()
    return render_template('movie.html', movie=movie)

# Страница поиска
@app.route('/search')
def search():
    # Здесь можно обрабатывать запросы поиска и получать данные из базы данных
    return render_template('search.html')

# Страница входа
@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', form=form)

# Страница регистрации
@app.route('/register')
def register():
    form = RegistrationForm()
    return render_template('register.html', form=form)

# Страница личного кабинета
@app.route('/profile')
def profile():
    # Здесь можно получать данные о пользователе из базы данных
    return render_template('profile.html')

# Обработка формы регистрации
@app.route('/register', methods=['POST'])
def register_post():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Здесь можно обрабатывать данные формы регистрации
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

# Обработка формы входа
@app.route('/login', methods=['POST'])
def login_post():
    form = LoginForm()
    if form.validate_on_submit():
        # Здесь можно обрабатывать данные формы входа
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

if __name__ == '__main__':
    from app.base_functions import create_tables

    #create_tables()
    app.run(debug=True)