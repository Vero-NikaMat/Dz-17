# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
        __tablename__ = 'movie'
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(255))
        description = db.Column(db.String(255))
        trailer = db.Column(db.String(255))
        year = db.Column(db.Integer)
        rating = db.Column(db.Float)
        genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
        genre = db.relationship("Genre")
        director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
        director = db.relationship("Director")

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()

class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()

class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

api = Api(app)
api.app.config['RESTFUL_JSON'] = {'ensure_ascii': False}
movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')

@movies_ns.route('/')
class MovieView(Resource):
    def get(self):
        all_movies = db.session.query(Movie)
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id is not None:
            all_movies = all_movies.filter(Movie.director_id == director_id)
        if genre_id is not None:
            all_movies = all_movies.filter(Movie.genre_id == genre_id)
        return movies_schema.dump(all_movies.all()), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "Фильм добавлен", 201


@movies_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid:int):
        try:
            movie = db.session.query(Movie).filter(Movie.id == uid).one()
            return movie_schema.dump(movie)
        except Exception:
            return "", 404


@directors_ns.route('/')
class DirectorView(Resource):
    def get(self):
        all_directors = db.session.query(Director).all()
        return directors_schema.dump(all_directors), 200

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return "Режиссер добавлен", 201

@directors_ns.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid:int):
        try:
            director = db.session.query(Director).filter(Director.id == uid).one()
            return director_schema.dump(director)
        except Exception:
            return "", 404

    def put(self, uid):
        director = db.session.quiery(Director).get(uid)
        req_json = request.json

        director.name = req_json.get("name")
        db.session.add(director)
        db.session.commit()
        return "Режиссер обновлен", 204

    def patch(self,uid):
        director = db.session.query(Director).get(uid)
        req_json = request.json

        if "name" in req_json:
            director.name = req_json.get("name")

        db.session.add(director)
        db.session.commit()

        return "Режиссер частично обновлен", 204

    def delete(self, uid:int):
        director = db.session.query(Director).get(uid)

        db.session.delete(director)
        db.session.commit()

        return "Режиссер удалён", 204


@genres_ns.route('/')
class GenreView(Resource):
    def get(self):
        all_genres = db.session.query(Genre).all()
        return genres_schema.dump(all_genres), 200

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)

        return "Жанр добавлен", 201


@genres_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid: int):
        try:
            genre = db.session.query(Genre).filter(Genre.id == uid).one()
            return genre_schema.dump(genre)
        except Exception:
            return "", 404

    def put(self, uid):
        genre = db.session.quiery(Genre).get(uid)
        req_json = request.json

        genre.name = req_json.get("name")

        db.session.add(genre)
        db.session.commit()

        return "Жанр обновлен", 204

    def patch(self, uid):
        genre = db.session.query(Genre).get(uid)
        req_json = request.json

        if "name" in req_json:
            genre.name = req_json.get("name")

        db.session.add(genre)
        db.session.commit()

        return "Жанр частично обновлен", 204

    def delete(self, uid: int):
        genre = db.session.query(Genre).get(uid)

        db.session.delete(genre)
        db.session.commit()

        return "Жанр удалён", 204

if __name__ == '__main__':
    app.run(debug=True)
