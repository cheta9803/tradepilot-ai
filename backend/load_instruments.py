from app.db.session import SessionLocal
from app.instruments.loader import InstrumentLoader

db = SessionLocal()

try:
    count = InstrumentLoader.sync(db)
    print(f"Imported {count} instruments.")
finally:
    db.close()