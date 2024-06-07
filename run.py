from flask import Flask, render_template, redirect, url_for, request, flash
from sqlalchemy import asc, desc
from app.database import Session
from app.models import User, Movie, Review
from forms import RegistrationForm, LoginForm, ReviewForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'HksolkdJJdhhduij3i3KKhjduh90jfj3JKL<NS'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Главная страница
@app.route('/')
def index():
    with Session() as session:
        top_movies = session.query(Movie).order_by(desc(Movie.rating)).limit(6).all()
        popular_movies = session.query(Movie).order_by(desc(Movie.reviews)).limit(6).all()
        session.close()
        return render_template('index.html', top_movies=top_movies, popular_movies=popular_movies)

@app.route('/category/<category>')
def category(category):
    with Session() as session:
        sort_option = request.args.get('sort', 'newest')

        sort_mapping = {
            'newest': desc(Movie.year),
            'oldest': asc(Movie.year),
            'rating': desc(Movie.rating),
            'reviews': desc(Movie.reviews),
            'title': asc(Movie.title)
        }
        sort_order = sort_mapping.get(sort_option, desc(Movie.year))

        if category == 'top':
            movies = session.query(Movie).order_by(sort_order).all()
            category_title = "Топ фильмов"
        elif category == 'popular':
            movies = session.query(Movie).order_by(sort_order).all()
            category_title = "Популярные фильмы"
        else:
            movies = []
            category_title = "Неизвестная категория"

        session.close()
        return render_template('category.html', movies=movies, category_title=category_title, category=category)

@app.route('/search_movies', methods=['GET'])
def search_movies():
    with Session() as session:
        db = session
        query = request.args.get('query', '')
        try:
            results = db.query(Movie).filter(Movie.title.ilike(f'%{query}%')).all()
            if results:
                return render_template('search_results.html', movies=results)
            else:
                return render_template('search_results.html', message="Фильм не найден")
        finally:
            db.close()

# Страница с информацией о фильме
@app.route('/movie/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def movie(movie_id):
    session = Session()
    movie = session.query(Movie).get(movie_id)
    form = ReviewForm()
    if form.validate_on_submit():
        user = session.query(User).get(current_user.id)
        review = Review(content=form.content.data, author=user, movie=movie)
        session.add(review)
        session.commit()
        flash('Ваш отзыв был добавлен!', 'success')
        return redirect(url_for('movie', movie_id=movie.id))
    reviews = session.query(Review).filter_by(movie_id=movie.id).all()
    return render_template('movie.html', movie=movie, form=form, reviews=reviews)

@login_manager.user_loader
def load_user(user_id):
    db = Session()
    return db.query(User).get(int(user_id))

# Страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with Session() as session:
            user = session.query(User).filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('index'))
            else:
                flash('Не верно введён логин или пароль. Пожалуйста, проверьте корректность данных', 'danger')
    return render_template('login.html', title='Login', form=form)

# Страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        with Session() as session:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            session.add(user)
            session.commit()
            flash('Вы успешно создали аккаунт!', 'success')
            return redirect(url_for('login'))
    else:
        # Исправлял ошибки
        # if form.errors:
        #     for field, errors in form.errors.items():
        #         for error in errors:
        #             flash(f"Ошибка в поле {getattr(form, field).label.text}: {error}", 'danger')
        return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Страница личного кабинета
@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    with Session() as session:
        user = session.query(User).get(user_id)
        if not user:
            flash('Пользователь не найден', 'danger')
            return redirect(url_for('index'))

        reviews = session.query(Review).filter_by(user_id=user_id).all()
        # Явная загрузка связанных фильмов
        for review in reviews:
            review.movie  # доступ к связанному фильму для загрузки данных
    
    return render_template('profile.html', user=user, reviews=reviews)


if __name__ == '__main__':
    from app.base_functions import create_tables

    #create_tables()
    app.run(debug=True)