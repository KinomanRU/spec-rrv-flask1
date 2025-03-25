from random import choice

from flask import Flask, jsonify, request

from about import about_me
from quotes import quotes

app = Flask(__name__)
app.json.ensure_ascii = False


@app.route("/")
def hello_world():
    return jsonify("Hello, World!")


@app.route("/about")
def about():
    return about_me


# Задание 1.1-1.2
@app.route("/quotes/")
@app.route("/quotes/<int:quote_id>")
def quote(quote_id=None):
    if quote_id:
        for quote in quotes:
            if quote["id"] == quote_id:
                return quote
        return jsonify(f"Quote with id={quote_id} not found"), 404
    else:
        return quotes


# Задание 1.3
@app.route("/quotes/count")
def count():
    return {"count": len(quotes)}


# Задание 1.4
@app.route("/quotes/rand")
def rand():
    return choice(quotes)


def get_new_id():
    return quotes[-1]["id"] + 1


def is_rating_valid(rating):
    return 1 <= rating <= 5


# Задание 2.1
@app.route("/quotes", methods=["POST"])
def create_quote():
    data = request.json
    try:
        rating = 1
        if is_rating_valid(data["rating"]):
            rating = data["rating"]
        quotes.append(
            {
                "id": get_new_id(),
                "author": data["author"],
                "text": data["text"],
                "rating": rating,
            }
        )
        return quotes, 201
    except KeyError:
        return jsonify("Not enough data"), 400


# Задание 2.4
@app.route("/quotes/<int:id>", methods=["PUT"])
def edit_quote(id):
    for quote in quotes:
        if quote["id"] == id:
            new_data = request.json
            for key in new_data.keys():
                if key == "rating" and is_rating_valid(new_data[key]):
                    quote[key] = new_data[key]
                elif key in quote.keys() and key not in ("id", "rating"):
                    quote[key] = new_data[key]
            return quote, 200
    return jsonify("Quote not found"), 404


# Задание 2.5
@app.route("/quotes/<int:id>", methods=["DELETE"])
def delete(id):
    for i, quote in enumerate(quotes):
        if quote["id"] == id:
            del quotes[i]
            return jsonify(f"Quote with id {id} is deleted."), 200
    return jsonify("Quote not found"), 404


# Доп. задание 2.2
@app.route("/filter")
def filter():
    args = request.args.to_dict()
    if not args:
        return quotes, 200
    for key, value in args.items():
        if key in ("id", "rating"):
            args[key] = int(value)
    result = []
    for quote in quotes:
        for key, value in args.items():
            if quote[key] == value:
                match = True
            else:
                match = False
                break
        if match:
            result.append(quote)
    return result, 200


if __name__ == "__main__":
    app.run(debug=True)
