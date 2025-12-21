from app import app, db
from models_marketplace import MarketPrice

with app.app_context():
    crops = ["Mustard", "Soybean", "Groundnut"]

    buyers = [
        ("Bharatpur Aggregators", 3, 5450),
        ("Alwar Procurement", 15, 5420),
        ("Tonk Oil Mills", 22, 5400)
    ]

    for crop in crops:
        for name, dist, price in buyers:
            db.session.add(MarketPrice(
                crop_name=crop,
                buyer_name=name,
                distance_km=dist,
                price=price
            ))

    db.session.commit()
    print("Seeded market prices")
