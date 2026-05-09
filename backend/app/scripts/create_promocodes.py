from app.database import SessionLocal
from app.models.promocodes import Promocode

PROMOCODES = [

    ("LIVER200", 200),
    ("HEPA200", 200),
    ("HISTOLOVE", 200),

    ("BIO100", 100),
    ("SVS100", 100),
]

db = SessionLocal()
for code, reward in PROMOCODES:
    exists = db.query(Promocode).filter(Promocode.code == code).first()
    if exists:
        continue
    promocode = Promocode(code=code, reward=reward, max_usages=2)
    db.add(promocode)

db.commit()
db.close()
print("Promocodes created")
