"""Add gamification and redemption store models

Revision ID: 567f8c9a1b3d
Revises: 434f490538b0
Create Date: 2025-12-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '567f8c9a1b3d'
down_revision = '434f490538b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### Add coins_earned column to farmers table ###
    with op.batch_alter_table('farmers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('coins_earned', sa.Integer(), default=0, nullable=True))

    # ### Create coin_balances table ###
    op.create_table(
        'coin_balances',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('farmer_id', sa.String(length=36), nullable=False),
        sa.Column('total_coins', sa.Integer(), default=0, nullable=True),
        sa.Column('available_coins', sa.Integer(), default=0, nullable=True),
        sa.Column('redeemed_coins', sa.Integer(), default=0, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['farmer_id'], ['farmers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('farmer_id')
    )

    # ### Create coin_transactions table ###
    op.create_table(
        'coin_transactions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('coin_balance_id', sa.String(length=36), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('related_type', sa.String(length=50), nullable=True),
        sa.Column('related_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['coin_balance_id'], ['coin_balances.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # ### Create redemption_offers table ###
    op.create_table(
        'redemption_offers',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('coin_cost', sa.Integer(), nullable=False),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=7), default='#388e3c', nullable=True),
        sa.Column('offer_type', sa.String(length=50), nullable=True),
        sa.Column('actual_value', sa.String(length=255), nullable=True),
        sa.Column('validity_days', sa.Integer(), default=90, nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
        sa.Column('stock_limit', sa.Integer(), nullable=True),
        sa.Column('stock_redeemed', sa.Integer(), default=0, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # ### Create farmer_redemptions table ###
    op.create_table(
        'farmer_redemptions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('farmer_id', sa.String(length=36), nullable=False),
        sa.Column('offer_id', sa.String(length=36), nullable=False),
        sa.Column('coins_spent', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), default='active', nullable=True),
        sa.Column('redeemed_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('redemption_code', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['farmer_id'], ['farmers.id'], ),
        sa.ForeignKeyConstraint(['offer_id'], ['redemption_offers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('redemption_code')
    )


def downgrade():
    # ### Drop tables in reverse order ###
    op.drop_table('farmer_redemptions')
    op.drop_table('redemption_offers')
    op.drop_table('coin_transactions')
    op.drop_table('coin_balances')

    # ### Remove coins_earned from farmers table ###
    with op.batch_alter_table('farmers', schema=None) as batch_op:
        batch_op.drop_column('coins_earned')
