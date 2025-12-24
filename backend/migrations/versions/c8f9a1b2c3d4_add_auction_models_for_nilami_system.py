"""Add auction models for nilami system

Revision ID: c8f9a1b2c3d4
Revises: iot_enhancements_002
Create Date: 2025-12-24 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8f9a1b2c3d4'
down_revision = 'iot_enhancements_002'
branch_labels = None
depends_on = None


def upgrade():
    # Create auctions table
    op.create_table('auctions',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('farmer_id', sa.String(length=36), nullable=False),
    sa.Column('crop_name', sa.String(length=100), nullable=False),
    sa.Column('quantity_quintals', sa.Float(), nullable=False),
    sa.Column('quality_grade', sa.String(length=50), nullable=True),
    sa.Column('base_price_per_quintal', sa.Float(), nullable=False),
    sa.Column('minimum_bid_increment', sa.Float(), nullable=True),
    sa.Column('current_highest_bid', sa.Float(), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('location', sa.String(length=255), nullable=True),
    sa.Column('district', sa.String(length=100), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('harvest_date', sa.Date(), nullable=True),
    sa.Column('storage_location', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.ForeignKeyConstraint(['farmer_id'], ['farmers.id'], ondelete='CASCADE')
    )
    
    # Create bids table
    op.create_table('bids',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('auction_id', sa.String(length=36), nullable=False),
    sa.Column('buyer_id', sa.String(length=36), nullable=False),
    sa.Column('bid_price_per_quintal', sa.Float(), nullable=False),
    sa.Column('bid_total_amount', sa.Float(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.ForeignKeyConstraint(['auction_id'], ['auctions.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['buyer_id'], ['buyers.id'], ondelete='CASCADE')
    )
    
    # Create counter_offers table
    op.create_table('counter_offers',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('auction_id', sa.String(length=36), nullable=False),
    sa.Column('bid_id', sa.String(length=36), nullable=True),
    sa.Column('buyer_id', sa.String(length=36), nullable=False),
    sa.Column('counter_price_per_quintal', sa.Float(), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.ForeignKeyConstraint(['auction_id'], ['auctions.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['bid_id'], ['bids.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['buyer_id'], ['buyers.id'], ondelete='CASCADE')
    )
    
    # Create auction_notifications table
    op.create_table('auction_notifications',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('user_type', sa.String(length=50), nullable=False),
    sa.Column('auction_id', sa.String(length=36), nullable=False),
    sa.Column('notification_type', sa.String(length=100), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('is_read', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.ForeignKeyConstraint(['auction_id'], ['auctions.id'], ondelete='CASCADE')
    )


def downgrade():
    # Drop tables in reverse order
    op.drop_table('auction_notifications')
    op.drop_table('counter_offers')
    op.drop_table('bids')
    op.drop_table('auctions')
