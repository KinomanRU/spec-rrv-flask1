from random import choice

from flask import Flask

from about import about_me
from quotes import quotes

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/about")
def about():
    return about_me


# Задание 1-2
@app.route("/quotes/")
@app.route("/quotes/<int:quote_id>")
def quote(quote_id=None):
    if quote_id:
        for quote in quotes:
            if quote["id"] == quote_id:
                return quote
        return f"Quote with id={quote_id} not found", 404
    else:
        return quotes


# Задание 3
@app.route("/count")
def count():
    return {"count": len(quotes)}


# Задание 4
@app.route("/rand")
def rand():
    return quotes[choice(range(len(quotes)))]


if __name__ == "__main__":
    app.run(debug=True)
