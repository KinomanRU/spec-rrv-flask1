import sqlite3
from pathlib import Path
from http import HTTPStatus

from flask import Flask, jsonify, request

from about import about_me

BASE_DIR = Path(__file__).parent
path_to_db = BASE_DIR / "store.db"

app = Flask(__name__)
app.json.ensure_ascii = False

connection = sqlite3.connect(path_to_db)


@app.route("/")
def hello_world():
    return jsonify("Hello, World!")


@app.route("/about")
def about():
    return about_me


# SELECT
@app.route("/quotes/")
@app.route("/quotes/<int:quote_id>")
def get_quote(quote_id=None):
    select_quotes = "SELECT * FROM quotes t"
    if quote_id is not None:
        select_quotes += " WHERE t.id = :1"
    connection = sqlite3.connect("store.db")
    cursor = connection.cursor()
    if quote_id is None:
        cursor.execute(select_quotes)
    else:
        cursor.execute(select_quotes, {"1": quote_id} if quote_id else None)
    quotes_db = cursor.fetchall()
    if len(quotes_db) == 0:
        return jsonify("Quote not found"), HTTPStatus.NOT_FOUND
    cursor.close()
    connection.close()
    keys = (
        "id",
        "author",
        "text",
        "rating",
    )
    quotes = []
    for quote_db in quotes_db:
        quotes.append(dict(zip(keys, quote_db)))
    return jsonify(quotes)


def is_rating_valid(rating):
    return 1 <= rating <= 5


# INSERT
@app.route("/quotes", methods=["POST"])
def create_quote():
    data = request.json
    try:
        connection = sqlite3.connect("store.db")
        cursor = connection.cursor()
        if not is_rating_valid(data["rating"]):
            data["rating"] = 1
        cursor.execute(
            "INSERT INTO quotes (author, text, rating) VALUES (:author, :text, :rating)",
            data,
        )
        connection.commit()
        cursor.close()
        connection.close()
        return get_quote(), HTTPStatus.CREATED
    except KeyError:
        return jsonify("Not enough data"), HTTPStatus.BAD_REQUEST


# UPDATE
@app.route("/quotes/<int:id>", methods=["PUT"])
def edit_quote(id):
    new_data = request.json
    connection = sqlite3.connect("store.db")
    cursor = connection.cursor()
    update_str = "UPDATE quotes SET"
    keys = new_data.keys()
    if "author" in keys:
        update_str += " author = '" + new_data["author"] + "',"
    if "text" in keys:
        update_str += " text = '" + new_data["text"] + "',"
    if "rating" in keys:
        update_str += " rating = " + str(new_data["rating"]) + ","
    update_str = update_str.rstrip(",") + " WHERE id = :id"
    cursor.execute(update_str, {"id": id})
    connection.commit()
    row_count = cursor.rowcount
    cursor.close()
    connection.close()
    if row_count > 0:
        return get_quote(), HTTPStatus.OK
    else:
        return jsonify("Quote not found"), HTTPStatus.NOT_FOUND


# DELETE
@app.route("/quotes/<int:id>", methods=["DELETE"])
def delete(id):
    connection = sqlite3.connect("store.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM quotes WHERE id = :id", {"id": id})
    connection.commit()
    row_count = cursor.rowcount
    cursor.close()
    connection.close()
    if row_count == 0:
        return jsonify("Quote not found"), HTTPStatus.NOT_FOUND
    else:
        return jsonify(f"Quote with {id=} is deleted."), HTTPStatus.OK


if __name__ == "__main__":
    app.run(debug=True)
