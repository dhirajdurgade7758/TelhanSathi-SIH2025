"""Restructure buyer_offers model

Revision ID: af9cd1edc680
Revises: 199be9da0596
Create Date: 2025-12-08 22:05:34.471418

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'af9cd1edc680'
down_revision = '199be9da0596'
branch_labels = None
depends_on = None


def upgrade():
    # Use raw SQL to avoid batch_alter_table circular dependency issues
    op.execute('''
        CREATE TABLE buyer_offers_new (
            id VARCHAR(36) NOT NULL PRIMARY KEY,
            buyer_id VARCHAR(36),
            buyer_name VARCHAR(255),
            buyer_mobile VARCHAR(20),
            buyer_location VARCHAR(255),
            buyer_company VARCHAR(255),
            crop_name VARCHAR(100) NOT NULL DEFAULT 'Unknown',
            quantity_quintal FLOAT NOT NULL DEFAULT 0,
            location_wanted VARCHAR(255),
            district_wanted VARCHAR(100),
            initial_price FLOAT NOT NULL,
            final_price FLOAT,
            sell_request_id VARCHAR(36),
            status VARCHAR(20) DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            FOREIGN KEY(buyer_id) REFERENCES buyers(id),
            FOREIGN KEY(sell_request_id) REFERENCES sell_requests(id)
        )
    ''')
    
    # Copy data from old table to new table
    op.execute('''
        INSERT INTO buyer_offers_new 
        (id, buyer_id, buyer_name, buyer_mobile, buyer_location, initial_price, final_price, status, created_at)
        SELECT id, buyer_id, buyer_name, buyer_mobile, buyer_location, initial_price, final_price, status, created_at
        FROM buyer_offers
    ''')
    
    # Drop old table
    op.execute('DROP TABLE buyer_offers')
    
    # Rename new table
    op.execute('ALTER TABLE buyer_offers_new RENAME TO buyer_offers')


def downgrade():
    # Create old table schema
    op.execute('''
        CREATE TABLE buyer_offers_new (
            id VARCHAR(36) NOT NULL PRIMARY KEY,
            listing_id VARCHAR(36) NOT NULL,
            buyer_id VARCHAR(36),
            buyer_name VARCHAR(255),
            buyer_mobile VARCHAR(20),
            buyer_location VARCHAR(255),
            initial_price FLOAT,
            final_price FLOAT,
            status VARCHAR(20) DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(listing_id) REFERENCES crop_listings(id),
            FOREIGN KEY(buyer_id) REFERENCES buyers(id)
        )
    ''')
    
    # Copy data back (without new columns)
    op.execute('''
        INSERT INTO buyer_offers_new
        (id, buyer_id, buyer_name, buyer_mobile, buyer_location, initial_price, final_price, status, created_at)
        SELECT id, buyer_id, buyer_name, buyer_mobile, buyer_location, initial_price, final_price, status, created_at
        FROM buyer_offers
    ''')
    
    # Drop new table
    op.execute('DROP TABLE buyer_offers')
    
    # Rename back
    op.execute('ALTER TABLE buyer_offers_new RENAME TO buyer_offers')
