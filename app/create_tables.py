from app.database import Base, engine, SessionLocal
from app.models import (
    StockIndex,
    StockBATMMAAN,
)
import json
import os

Base.metadata.create_all(bind=engine)


def load_initial_data():
    db = SessionLocal()

    index_path = os.path.join("app", "data", "stock_index.json")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            index_data = json.load(f)
            for item in index_data:
                if not db.query(StockIndex).filter_by(Ticker=item["Ticker"]).first():
                    db.add(
                        StockIndex(
                            Ticker=item["Ticker"],
                            Name=item["Name"],
                            query=item.get("query", ""),
                        )
                    )

    batmmaan_path = os.path.join("app", "data", "stock_BATMMAAN.json")
    if os.path.exists(batmmaan_path):
        with open(batmmaan_path, "r", encoding="utf-8") as f:
            stock_data = json.load(f)
            for item in stock_data:
                if not db.query(StockBATMMAAN).filter_by(Ticker=item["Ticker"]).first():
                    db.add(
                        StockBATMMAAN(
                            Ticker=item["Ticker"],
                            Name=item["Name"],
                            query=item.get("query", ""),
                        )
                    )

    db.commit()
    db.close()


load_initial_data()
