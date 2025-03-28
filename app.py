from http import HTTPStatus
from pathlib import Path

from flask import Flask, jsonify, request, abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.exceptions import HTTPException

from about import about_me


class Base(DeclarativeBase):
    pass


BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.json.ensure_ascii = False
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR / 'quotes.db'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(model_class=Base)
db.init_app(app)

migrate = Migrate(app, db)


class AuthorModel(db.Model):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    surname: Mapped[str] = mapped_column(String(32), nullable=True)
    quotes: Mapped[list["QuoteModel"]] = relationship(
        back_populates="author",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __init__(self, name, surname=None):
        self.name = name
        self.surname = surname

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
        }


class QuoteModel(db.Model):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped["AuthorModel"] = relationship(back_populates="quotes")
    text: Mapped[str] = mapped_column(String(255))
    rating: Mapped[int] = mapped_column(default=1)

    def __init__(self, author, text, rating=None):
        self.author = author
        self.text = text
        self.rating = rating

    def to_dict(self):
        return {
            "id": self.id,
            "author_id": self.author_id,
            "text": self.text,
            "rating": self.rating,
        }


@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"message": e.description}), e.code


@app.route("/")
def hello_world():
    return jsonify("Hello, World!")


@app.route("/about")
def about():
    return about_me


def get_author_by_id(author_id):
    return db.get_or_404(
        AuthorModel,
        author_id,
        description=f"Author with id={author_id} not found",
    )


def get_quote_by_id(quote_id):
    return db.get_or_404(
        QuoteModel,
        quote_id,
        description=f"Quote with id={quote_id} not found",
    )


def is_rating_valid(rating):
    return 1 <= rating <= 5


# CREATE AUTHOR
@app.route("/authors", methods=["POST"])
def create_author():
    try:
        json_data = request.json
        attrs = set(json_data.keys()) & {"name", "surname"}
        if not attrs or "name" not in attrs:
            abort(HTTPStatus.BAD_REQUEST, "Attribute 'name' is required")
        author_name: str = ""
        author_surname: str = ""
        for attr in attrs:
            if attr == "name":
                author_name = json_data[attr]
            if attr == "surname":
                author_surname = json_data[attr]
        author = AuthorModel(
            author_name,
            author_surname,
        )
        db.session.add(author)
        db.session.commit()
        return jsonify(author.to_dict()), HTTPStatus.CREATED
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, str(e))


# EDIT AUTHOR
@app.route("/authors/<int:author_id>", methods=["PUT"])
def edit_author(author_id: int):
    try:
        author = get_author_by_id(author_id)
        json_data = request.json
        attrs = set(json_data.keys()) & {"name", "surname"}
        if not attrs:
            abort(HTTPStatus.BAD_REQUEST, "Nothing to update")
        for attr in attrs:
            if attr == "name":
                author.name = json_data[attr]
            if attr == "surname":
                author.surname = json_data[attr]
        db.session.commit()
        return jsonify(author.to_dict())
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, str(e))


# GET ALL AUTHORS
@app.route("/authors", methods=["GET"])
def get_authors():
    authors = db.session.scalars(db.select(AuthorModel)).all()
    return jsonify([author.to_dict() for author in authors])


# GET ONE AUTHOR
@app.route("/authors/<int:author_id>", methods=["GET"])
def get_author(author_id: int):
    author = get_author_by_id(author_id)
    return jsonify(author.to_dict())


# DELETE AUTHOR
@app.route("/authors/<int:author_id>", methods=["DELETE"])
def delete_author(author_id: int):
    try:
        author = get_author_by_id(author_id)
        db.session.delete(author)
        db.session.commit()
        return get_authors()
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, str(e))


# CREATE QUOTE
@app.route("/authors/<int:author_id>/quotes", methods=["POST"])
def create_quote(author_id: int):
    try:
        author = get_author_by_id(author_id)
        json_data = request.json
        attrs = set(json_data.keys()) & {"text", "rating"}
        if not attrs or "text" not in attrs:
            abort(HTTPStatus.BAD_REQUEST, "Attribute 'text' is required")
        quote_text: str = ""
        quote_rating: int = 1
        for attr in attrs:
            if attr == "text":
                quote_text = json_data[attr]
            if attr == "rating" and is_rating_valid(int(json_data[attr])):
                quote_rating = int(json_data[attr])
        quote = QuoteModel(
            author,
            quote_text,
            quote_rating,
        )
        db.session.add(quote)
        db.session.commit()
        return jsonify(quote.to_dict()), HTTPStatus.CREATED
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, str(e))


# EDIT QUOTE
@app.route("/quotes/<int:quote_id>", methods=["PUT"])
def edit_quote(quote_id: int):
    try:
        quote = get_quote_by_id(quote_id)
        json_data = request.json
        attrs = set(json_data.keys()) & {"author_id", "text", "rating"}
        if not attrs:
            abort(HTTPStatus.BAD_REQUEST, "Nothing to update")
        for attr in attrs:
            if attr == "author_id":
                quote.author_id = int(json_data[attr])
            if attr == "text":
                quote.text = json_data[attr]
            if attr == "rating" and is_rating_valid(int(json_data[attr])):
                quote.rating = int(json_data[attr])
        db.session.commit()
        return jsonify(quote.to_dict())
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, str(e))


# GET ALL QOUTES
@app.route("/quotes", methods=["GET"])
def get_quotes():
    quotes = db.session.scalars(db.select(QuoteModel)).all()
    return jsonify([quote.to_dict() for quote in quotes])


# GET ONE QUOTE
@app.route("/quotes/<int:quote_id>", methods=["GET"])
def get_quote(quote_id: int):
    quote = get_quote_by_id(quote_id)
    return jsonify(quote.to_dict())


# DELETE QUOTE
@app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id: int):
    try:
        quote = get_quote_by_id(quote_id)
        db.session.delete(quote)
        db.session.commit()
        return get_quotes()
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, str(e))


# GET ALL QUOTES BY AUTHOR
@app.route("/authors/<int:author_id>/quotes", methods=["GET"])
def get_author_quotes(author_id: int):
    author = get_author_by_id(author_id)
    quotes = author.quotes
    return jsonify(
        author=author.to_dict(),
        quotes=[quote.to_dict() for quote in quotes],
    )


if __name__ == "__main__":
    app.run(debug=True)
