from app import app, db, QuoteModel
from quotes import quotes

q1 = QuoteModel("Народная мудрость", "Нет пламя без огня")
with app.app_context():
    db.session.add(q1)
    for quote in quotes:
        db.session.add(
            QuoteModel(
                quote["author"],
                quote["text"],
                quote["rating"],
            )
        )
    db.session.commit()


with app.app_context():
    quotes = db.session.scalars(db.select(QuoteModel)).all()
    print(quotes)
