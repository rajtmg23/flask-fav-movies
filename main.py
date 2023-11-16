from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
# CREATE DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)



# CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


# with app.app_context():
#     db.create_all()


class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating out of 10: eg. 7.5")
    review = StringField("Your Review:")
    submit = SubmitField("Done")


class AddMovie(FlaskForm):
    title = StringField("Add new movie name:", validators=[DataRequired()])
    submit = SubmitField("Add Movie")

"""
# Add new Record
new_movie = Movie(
    title="Phone Booth",
    year=2002,
    description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    rating=7.3,
    ranking=10,
    review="My favourite character was the caller.",
    img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
)

with app.app_context():
    db.session.add(new_movie)
    db.session.commit()
"""

@app.route("/")
def home():
    # movies_list = db.session.query(Movie).all()
    movies_list = Movie.query.order_by(Movie.rating).all()
    # This line loops through all the movies
    for i in range(len(movies_list)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        movies_list[i].ranking = len(movies_list) - i
    db.session.commit()
    return render_template("index.html", movies=movies_list)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    form = RateMovieForm()
    movie_id = request.args.get('id')
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit.html', movie=movie, form=form)


@app.route('/del')
def delete():
    movie_id = request.args.get('id')
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


tmdb_api = "681539f9587e812081f2a55d6313ad42"
base_url = "https://api.themoviedb.org/3/search/movie"
@app.route('/add', methods=["GET", "POST"])
def add_movie():
    new_form = AddMovie()
    if new_form.validate_on_submit():
        movie_search = new_form.title.data
        params = {"api_key": tmdb_api, "query": movie_search}
        # response = requests.get(base_url, params=params)
        movies_list = requests.get(base_url, params=params).json()['results']
        return render_template('select.html', movies=movies_list)
    return render_template('add.html', form=new_form)


movie_search_url = "https://api.themoviedb.org/3/movie"
poster_search_url = "https://image.tmdb.org/t/p/w500"
@app.route('/select')
def select_movie():
    movie_api_id = request.args.get('id')
    if movie_api_id:
        movie_info_url = f"{movie_search_url}/{movie_api_id}"
        params = {"api_key": tmdb_api}
        movie_info = requests.get(movie_info_url, params=params).json()
        new_movie = Movie(
            title = movie_info['title'],
            year = movie_info['release_date'].split('-')[0],
            img_url = f"{poster_search_url}/{movie_info['poster_path']}",
            description = movie_info['overview']
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('edit', id=new_movie.id))



if __name__ == '__main__':
    app.run(debug=True)
