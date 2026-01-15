from flask import Flask, jsonify
from sqlalchemy import create_engine, Column, Integer,text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import time

app = Flask(__name__)

# SQLite database
engine = create_engine(
    "sqlite:///inventory.db",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Inventory table
class Inventory(Base):
    __tablename__ = "inventory"
    item_id = Column(Integer, primary_key=True)
    stock = Column(Integer, nullable=False)

# Purchase record table
class Purchase(Base):
    __tablename__ = "purchase"
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize stock if not exists
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
        session.execute(text("BEGIN IMMEDIATE"))  # DATABASE LOCK

        item = session.query(Inventory).filter_by(item_id=1).first()

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
        time.sleep(0.01)  # backoff
        return jsonify({"message": "Retry"}), 503

    finally:
        session.close()

if __name__ == "__main__":
    app.run(threaded=True)
