import uuid
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from extensions import db
from models import Farmer
from models_marketplace import CropListing, BuyerOffer, MarketPrice, SellPhoto, SellRequest

market_bp = Blueprint("market", __name__, url_prefix="/market")


# Allowed crops
OILSEEDS = [
    "Mustard", "Soybean", "Groundnut", "Sunflower",
    "Castor", "Sesame", "Linseed", "Safflower", "Niger Seed"
]


@market_bp.route("/select-crop")
def select_crop():
    if "farmer_id_verified" not in session:
        return redirect(url_for("auth.login"))

    # Check if a specific crop was passed via query parameter
    selected_crop = request.args.get('crop', None)
    
    if selected_crop:
        # If crop is specified, redirect to the seller listings page for that crop
        return redirect(url_for("market.crop_sellers", crop=selected_crop))
    
    return render_template("market_select_crop.html", crops=OILSEEDS)


@market_bp.route("/sellers/<crop>")
def crop_sellers(crop):
    """Display all sellers/listings for a specific crop"""
    if "farmer_id_verified" not in session:
        return redirect(url_for("auth.login"))
    
    crop = crop.strip()
    
    # Get all crop listings for this crop
    listings = SellRequest.query.filter_by(crop_name=crop).all()
    
    # Calculate average price
    if listings:
        avg_price = sum(l.expected_price for l in listings) / len(listings)
    else:
        avg_price = 0
    
    return render_template("market_sellers.html", crop=crop, listings=listings, avg_price=int(avg_price))


# @market_bp.route("/nearby/<crop>")
# def nearby_prices(crop):
#     crop = crop.strip()
#     prices = MarketPrice.query.filter_by(crop_name=crop).all()
    
#     if not prices:
#         # Fallback default data
#         prices = [
#             dict(buyer_name="Bharatpur Aggregators", distance_km=3, price=5450),
#             dict(buyer_name="Alwar Procurement Page", distance_km=15, price=5420),
#             dict(buyer_name="Tonk Oil Mills", distance_km=22, price=5400),
#             dict(buyer_name="Jaipur Digital Hub", distance_km=50, price=5380),
#             dict(buyer_name="Farmer Connect Platform", distance_km=8, price=5410),
#         ]
#         avg_price = 5432
#     else:
#         avg_price = sum(p.price for p in prices) / len(prices)
    
#     today = datetime.now().strftime("%d %b %Y")

#     return render_template("market_nearby.html", crop=crop, prices=prices, avg_price=int(avg_price), today=today)


@market_bp.route("/list", methods=["POST"])
def create_listing():
    if "farmer_id_verified" not in session:
        return jsonify({"error": "Not logged in"}), 401

    farmer = Farmer.query.filter_by(id=session["farmer_id_verified"]).first()

    crop_name = request.form.get("crop_name")
    quantity = float(request.form.get("quantity"))
    expected_price = float(request.form.get("expected_price"))
    harvest_date = datetime.strptime(request.form.get("harvest_date"), "%Y-%m-%d")

    # Photos
    uploads_dir = "static/uploads"
    os.makedirs(uploads_dir, exist_ok=True)

    def save_photo(photo):
        if not photo:
            return None
        filename = secure_filename(photo.filename)
        path = os.path.join(uploads_dir, f"{uuid.uuid4()}_{filename}")
        photo.save(path)
        return path

    p1 = save_photo(request.files.get("photo1"))
    p2 = save_photo(request.files.get("photo2"))
    p3 = save_photo(request.files.get("photo3"))

    listing = CropListing(
        farmer_id=farmer.id,
        crop_name=crop_name,
        quantity_quintal=quantity,
        expected_price=expected_price,
        harvest_date=harvest_date,
        photo1_path=p1,
        photo2_path=p2,
        photo3_path=p3
    )

    db.session.add(listing)
    db.session.commit()

    return redirect(url_for("market.deal_status", listing_id=listing.id))


@market_bp.route("/deal/<listing_id>")
def deal_status(listing_id):
    listing = CropListing.query.get_or_404(listing_id)
    offer = BuyerOffer.query.filter_by(listing_id=listing.id).order_by(
        BuyerOffer.created_at.desc()
    ).first()

    return render_template("market_deal_status.html", listing=listing, offer=offer)


@market_bp.route("/offer/<listing_id>", methods=["POST"])
def buyer_offer(listing_id):
    listing = CropListing.query.get_or_404(listing_id)

    final_price = float(request.form.get("final_price"))
    status = request.form.get("status")  # accept / decline

    offer = BuyerOffer(
        listing_id=listing.id,
        buyer_name="Kisan Shakti FPO",
        buyer_mobile="9876543210",
        buyer_location="District Office",
        initial_price=listing.expected_price,
        final_price=final_price,
        status=status,
    )

    # Update listing status
    listing.status = status

    db.session.add(offer)
    db.session.commit()

    return jsonify({"success": True})

@market_bp.route("/nearby/<crop>")
def market_nearby(crop):
    crop = crop.strip()
    offer = BuyerOffer.query.all()
    for o in offer:
        print(o.crop_name)
    # Fetch buyer offers for this crop (filter by exact crop name)
    print(f"DEBUG: Searching for crop containing '{crop}'")
    buyer_offers = BuyerOffer.query.filter(
        BuyerOffer.crop_name.ilike(f'%{crop}%'),
        BuyerOffer.status == 'pending'
    ).all()
    print(f"DEBUG: Found {len(buyer_offers)} offers")

    # Convert BuyerOffer objects to dict format for template
    prices = []
    for offer in buyer_offers:
        prices.append({
            'buyer_name': offer.buyer_name or offer.buyer_company or 'Buyer',
            'distance_km': 0,  # No distance info from buyer offers
            'price': offer.initial_price,
            'offer_id': offer.id,
            'buyer_location': offer.buyer_location,
            'buyer_mobile': offer.buyer_mobile,
        })

    if not prices:
        # fallback default data (this helps UI work instantly)
        print("No buyer offers found, using fallback data.")
        db_prices = None
    else:
        db_prices = prices

    # Calculate average price
    if db_prices:
        avg_price = sum(p['price'] for p in db_prices) / len(db_prices)
    else:
        avg_price = 5432  # fallback
    return render_template(
        "market_nearby.html",
        crop=crop,
        avg_price=int(avg_price),
        prices=prices
    )

@market_bp.route("/deal/<request_id>")
def deal_review(request_id):
    req = SellRequest.query.filter_by(id=request_id).first_or_404()
    photos = SellPhoto.query.filter_by(request_id=request_id).all()

    return render_template("deal_review.html", req=req, photos=photos)

@market_bp.route("/deal/<request_id>/decline", methods=["POST"])
def deal_decline(request_id):
    req = SellRequest.query.get(request_id)
    req.status = "declined"
    db.session.commit()
    return {"success": True}

@market_bp.route("/deal/<request_id>/accept", methods=["POST"])
def deal_accept(request_id):
    req = SellRequest.query.get(request_id)

    final_price = float(request.json.get("final_price"))
    req.status = "accepted"
    req.buyer_price = final_price
    req.final_price = final_price

    db.session.commit()

    return {"success": True, "final_price": final_price}

@market_bp.route("/deal/<request_id>/farmer-confirm", methods=["POST"])
def deal_farmer_confirm(request_id):
    req = SellRequest.query.get(request_id)
    req.status = "final_confirmed"
    db.session.commit()
    return {"success": True}


# New Routes for Deal Review and Status Pages

@market_bp.route("/deal-review")
def deal_review_page():
    """Display the deal review page with image upload"""
    if "farmer_id_verified" not in session:
        return redirect(url_for("auth.login"))
    
    return render_template("deal_review.html")


@market_bp.route("/sell/create", methods=["POST"])
def create_sell_request():
    """Create a new sell request with photos"""
    if "farmer_id_verified" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    farmer = Farmer.query.filter_by(id=session["farmer_id_verified"]).first()
    if not farmer:
        return jsonify({"error": "Farmer not found"}), 404
    
    crop = request.form.get("crop")
    quantity = float(request.form.get("quantity"))
    expected_price = float(request.form.get("expected_price"))
    harvest_date = request.form.get("harvest_date")
    
    # Create uploads directory
    uploads_dir = "static/uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    
    def save_photo(photo):
        if not photo or photo.filename == '':
            return None
        filename = secure_filename(photo.filename)
        path = os.path.join(uploads_dir, f"{uuid.uuid4()}_{filename}")
        photo.save(path)
        return path
    
    # Save photos
    photo1 = save_photo(request.files.get("photo1"))
    photo2 = save_photo(request.files.get("photo2"))
    photo3 = save_photo(request.files.get("photo3"))
    
    # Create sell request
    sell_request = SellRequest(
        farmer_id=farmer.id,
        crop_name=crop,
        quantity_quintal=quantity,
        expected_price=expected_price,
        harvest_date=harvest_date,
        location=f"{farmer.village}, {farmer.district}",
        farmer_name=farmer.name,
        farmer_phone=farmer.phone_number,
        status="pending"
    )
    
    db.session.add(sell_request)
    db.session.flush()  # Get the ID before commit
    
    # Save photos
    if photo1:
        p1 = SellPhoto(request_id=sell_request.id, photo_url=photo1)
        db.session.add(p1)
    if photo2:
        p2 = SellPhoto(request_id=sell_request.id, photo_url=photo2)
        db.session.add(p2)
    if photo3:
        p3 = SellPhoto(request_id=sell_request.id, photo_url=photo3)
        db.session.add(p3)
    
    db.session.commit()
    
    return jsonify({"success": True, "request_id": sell_request.id}), 201


@market_bp.route("/all-deals")
def all_deals_page():
    """Display all deals for the farmer"""
    if "farmer_id_verified" not in session:
        return redirect(url_for("auth.login"))
    
    return render_template("all_deals.html")


@market_bp.route("/deals-list")
def deals_list():
    """API endpoint to get all deals for the logged-in farmer"""
    if "farmer_id_verified" not in session:
        return jsonify({"error": "Not logged in"}), 401
    # Return all sell requests and listings so the UI shows every requested selling
    sell_requests = SellRequest.query.all()
    listings = CropListing.query.all()

    combined = []

    for deal in sell_requests:
        print(deal.harvest_date)
        combined.append({
            "id": deal.id,
            "type": "sell_request",
            "farmer_id": deal.farmer_id,
            "crop_name": deal.crop_name,
            "quantity_quintal": deal.quantity_quintal,
            "expected_price": deal.expected_price,
            "buyer_price": deal.buyer_price,
            "harvest_date": deal.harvest_date,
            "status": deal.status,
            "created_at": deal.created_at.isoformat() if deal.created_at else None
        })

    for lst in listings:
        combined.append({
            "id": lst.id,
            "type": "listing",
            "farmer_id": lst.farmer_id,
            "crop_name": lst.crop_name,
            "quantity_quintal": lst.quantity_quintal,
            "expected_price": lst.expected_price,
            "buyer_price": None,
            "harvest_date": lst.harvest_date.isoformat() if lst.harvest_date else None,
            "status": lst.status,
            "created_at": lst.created_at.isoformat() if lst.created_at else None
        })

    # Sort combined by created_at desc (None values go last)
    def parse_created(item):
        try:
            return item["created_at"] or "0000-01-01T00:00:00"
        except Exception:
            return "0000-01-01T00:00:00"

    combined_sorted = sorted(combined, key=lambda x: parse_created(x), reverse=True)

    return jsonify(combined_sorted)


@market_bp.route("/deal-details/<request_id>")
def deal_details(request_id):
    """Display details of a specific deal"""
    if "farmer_id_verified" not in session:
        return redirect(url_for("auth.login"))
    
    deal = SellRequest.query.get_or_404(request_id)
    # Allow any logged-in farmer to view the deal details page.
    # The JSON API `/deal-data/<id>` will indicate ownership via `is_owner` and
    # the frontend will show appropriate actions.
    return render_template("market_deal_status.html")


@market_bp.route("/deal-data/<request_id>")
def deal_data(request_id):
    """API endpoint to get deal data as JSON"""
    if "farmer_id_verified" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    deal = SellRequest.query.get_or_404(request_id)
    # Return deal data to any logged-in farmer. Include `is_owner` so the
    # frontend can hide/show negotiation and action UI.
    photos = SellPhoto.query.filter_by(request_id=request_id).all()
    
    # Ensure harvest_date is serialized as ISO string (or left as string) and
    # attempt to provide a human-friendly location. Some older records may
    # have empty `location` field, so fall back to farmer's village/district.
    # Also handle the case where harvest_date is already a string (stored as
    # string in this model) or a date/datetime object.
    raw_harvest = deal.harvest_date
    if hasattr(raw_harvest, 'isoformat'):
        harvest_serialized = raw_harvest.isoformat()
    else:
        harvest_serialized = raw_harvest if raw_harvest else None

    # Fallback for location: prefer deal.location, otherwise try to lookup
    # farmer record and use village/district if available.
    location_val = deal.location
    if not location_val:
        try:
            from models import Farmer
            farmer_obj = Farmer.query.filter_by(id=deal.farmer_id).first()
            if farmer_obj:
                parts = []
                if getattr(farmer_obj, 'village', None):
                    parts.append(farmer_obj.village)
                if getattr(farmer_obj, 'district', None):
                    parts.append(farmer_obj.district)
                if parts:
                    location_val = ', '.join(parts)
        except Exception:
            # If anything fails, leave location_val as-is (None or empty)
            pass

    deal_data = {
        "id": deal.id,
        "crop_name": deal.crop_name,
        "quantity_quintal": deal.quantity_quintal,
        "expected_price": deal.expected_price,
        "buyer_price": deal.buyer_price,
        "final_price": deal.final_price,
        "harvest_date": harvest_serialized,
        "location": location_val,
        "farmer_name": deal.farmer_name,
        "farmer_id": deal.farmer_id,
        "farmer_phone": deal.farmer_phone,
        "status": deal.status,
        "created_at": deal.created_at.isoformat() if deal.created_at else None,
        "photos": [
            {
                "id": p.id,
                "photo_url": p.photo_url
            } for p in photos
        ]
    }
    # Indicate whether the currently logged-in farmer is the owner/requester
    current_farmer = session.get("farmer_id_verified")
    try:
        deal_data["is_owner"] = True if current_farmer and str(current_farmer) == str(deal.farmer_id) else False
    except Exception:
        deal_data["is_owner"] = False

    return jsonify(deal_data)
