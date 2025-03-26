from pathlib import Path
from http import HTTPStatus

from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String
from werkzeug.exceptions import HTTPException
from flask_migrate import Migrate

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


class QuoteModel(db.Model):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(32))
    text: Mapped[str] = mapped_column(String(255))
    rating: Mapped[int] = mapped_column(default=1)

    def __init__(self, author, text, rating=None):
        self.author = author
        self.text = text
        self.rating = rating

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
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


# GET ALL
@app.route("/quotes")
def get_quotes():
    quotes = db.session.scalars(db.select(QuoteModel)).all()
    return jsonify([quote.to_dict() for quote in quotes])


def get_quote_by_id(quote_id):
    return db.get_or_404(
        QuoteModel,
        quote_id,
        description=f"Quote with id={quote_id} not found",
    )


# GET ONE
@app.route("/quotes/<int:quote_id>")
def get_quote(quote_id):
    quote = get_quote_by_id(quote_id)
    return jsonify(quote.to_dict())


def is_rating_valid(rating):
    return 1 <= rating <= 5


# POST
@app.route("/quotes", methods=["POST"])
def create_quote():
    data = request.json
    attrs = data.keys()
    if "author" not in attrs or "text" not in attrs:
        abort(HTTPStatus.BAD_REQUEST, "Not enough attributes")
    author: str = ""
    text: str = ""
    rating: int = 1
    for attr in attrs:
        if attr == "author":
            author = data[attr]
        if attr == "text":
            text = data[attr]
        if attr == "rating" and is_rating_valid(data[attr]):
            rating = int(data[attr])
    quote = QuoteModel(
        author,
        text,
        rating,
    )
    db.session.add(quote)
    db.session.commit()
    return get_quotes(), HTTPStatus.CREATED


# PUT
@app.route("/quotes/<int:quote_id>", methods=["PUT"])
def edit_quote(quote_id):
    data = request.json
    attrs = set(data.keys()) & {"author", "text", "rating"}
    if not attrs:
        abort(HTTPStatus.BAD_REQUEST, "Nothing to update")
    quote = get_quote_by_id(quote_id)
    for attr in attrs:
        if attr == "author":
            quote.author = data[attr]
        if attr == "text":
            quote.text = data[attr]
        if attr == "rating" and is_rating_valid(data[attr]):
            quote.rating = int(data[attr])
    db.session.commit()
    return get_quote(quote_id)


# DELETE
@app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete(quote_id):
    quote = get_quote_by_id(quote_id)
    db.session.delete(quote)
    return get_quotes()


# FILTER
@app.route("/filter")
def set_filter():
    args = request.args.to_dict()
    attrs = args.keys() & {"author", "rating"}
    filters = {}
    for attr in attrs:
        filters[attr] = args[attr]
    quotes = db.session.scalars(db.select(QuoteModel).filter_by(**filters)).all()
    return jsonify([quote.to_dict() for quote in quotes])


if __name__ == "__main__":
    app.run(debug=True)
