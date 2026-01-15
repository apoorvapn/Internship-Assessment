

from flask import Flask, jsonify
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError

app = Flask(__name__)

DATABASE_URL = "postgresql://postgres:Apoorva#123@localhost:5432/inventory_db"

engine = create_engine(
    DATABASE_URL,
    isolation_level="READ COMMITTED",
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Inventory(Base):
    __tablename__ = "inventory"
    item_id = Column(Integer, primary_key=True)
    stock = Column(Integer, nullable=False)

class Purchase(Base):
    __tablename__ = "purchase"
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer)

Base.metadata.create_all(bind=engine)

def init_inventory():
    session = SessionLocal()
    item = session.query(Inventory).filter_by(item_id=1).first()
    if not item:
        session.add(Inventory(item_id=1, stock=100))
    session.commit()
    session.close()

init_inventory()

@app.route("/buy_ticket", methods=["POST"])
def buy_ticket():
    session = SessionLocal()
    try:
        # 🔒 ROW-LEVEL LOCK
        item = (
            session.query(Inventory)
            .filter_by(item_id=1)
            .with_for_update()
            .one()
        )

        if item.stock > 0:
            item.stock -= 1
            session.add(Purchase(item_id=1))
            session.commit()
            return jsonify({"message": "Purchase successful"}), 200
        else:
            session.rollback()
            return jsonify({"message": "Sold out"}), 410

    except OperationalError:
        session.rollback()
        return jsonify({"message": "Database busy"}), 503

    finally:
        session.close()

if __name__ == "__main__":
    app.run()

