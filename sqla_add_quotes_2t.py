from app import app, db, QuoteModel, AuthorModel
from quotes import quotes

with app.app_context():
    author: AuthorModel
    for quote in quotes:
        author = AuthorModel(quote["author"])
        db.session.add(author)
        db.session.add(
            QuoteModel(
                author,
                quote["text"],
                quote["rating"],
            )
        )
    author = AuthorModel("Народная мудрость")
    db.session.add(author)
    db.session.add(QuoteModel(author, "Нет пламя без огня"))
    db.session.commit()


with app.app_context():
    quotes = db.session.scalars(db.select(QuoteModel)).all()
    print(quotes)
