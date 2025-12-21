from models import Farmer
from extensions import db
f = Farmer.query.filter_by(farmer_id="567894251673").first()
f.onboarding_completed = False
db.session.commit()
