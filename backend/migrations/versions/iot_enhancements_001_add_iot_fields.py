"""Add enhanced IoT device and sensor fields

Revision ID: iot_enhancements_001
Revises: 5b4b6fd4005b
Create Date: 2025-12-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'iot_enhancements_001'
down_revision = '5b4b6fd4005b'
branch_labels = None
depends_on = None


def upgrade():
    # Modify sensor_readings table
    with op.batch_alter_table('sensor_readings', schema=None) as batch_op:
        # Add new columns if they don't exist
        batch_op.add_column(sa.Column('soil_temp', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('light_raw', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('rssi', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('uptime', sa.Integer(), nullable=True))
        # Create index on received_at for faster queries
        batch_op.create_index(batch_op.f('ix_sensor_readings_received_at'), ['received_at'], existing_ok=True)
    
    # Modify iot_devices table
    with op.batch_alter_table('iot_devices', schema=None) as batch_op:
        batch_op.add_column(sa.Column('device_mac', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('device_name', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), default=True))
        batch_op.add_column(sa.Column('last_seen', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('wifi_ssid', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('firmware_version', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('soil_dry_value', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('soil_wet_value', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        # Create unique index on device_mac
        batch_op.create_unique_constraint('uq_iot_devices_device_mac', ['device_mac'], existing_ok=True)
        # Create index on farmer_id for faster lookups
        batch_op.create_index(batch_op.f('ix_iot_devices_farmer_id'), ['farmer_id'], existing_ok=True)
    
    # Modify device_requests table
    with op.batch_alter_table('device_requests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('priority', sa.String(20), default='normal'))
        batch_op.add_column(sa.Column('land_area_hectares', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('field_location', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('preferred_installation_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('farmer_notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('admin_notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('scheduled_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('completed_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('assigned_device_id', sa.String(36), nullable=True))
        batch_op.create_index(batch_op.f('ix_device_requests_farmer_id'), ['farmer_id'], existing_ok=True)
        batch_op.create_index(batch_op.f('ix_device_requests_created_at'), ['created_at'], existing_ok=True)


def downgrade():
    # Remove added columns
    with op.batch_alter_table('device_requests', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_device_requests_created_at'), existing_ok=True)
        batch_op.drop_index(batch_op.f('ix_device_requests_farmer_id'), existing_ok=True)
        batch_op.drop_column('assigned_device_id')
        batch_op.drop_column('completed_date')
        batch_op.drop_column('scheduled_date')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('admin_notes')
        batch_op.drop_column('farmer_notes')
        batch_op.drop_column('preferred_installation_date')
        batch_op.drop_column('field_location')
        batch_op.drop_column('land_area_hectares')
        batch_op.drop_column('priority')
    
    with op.batch_alter_table('iot_devices', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_iot_devices_farmer_id'), existing_ok=True)
        batch_op.drop_constraint('uq_iot_devices_device_mac', type_='unique', existing_ok=True)
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('soil_wet_value')
        batch_op.drop_column('soil_dry_value')
        batch_op.drop_column('firmware_version')
        batch_op.drop_column('wifi_ssid')
        batch_op.drop_column('last_seen')
        batch_op.drop_column('is_active')
        batch_op.drop_column('device_name')
        batch_op.drop_column('device_mac')
    
    with op.batch_alter_table('sensor_readings', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_sensor_readings_received_at'), existing_ok=True)
        batch_op.drop_column('uptime')
        batch_op.drop_column('rssi')
        batch_op.drop_column('light_raw')
        batch_op.drop_column('soil_temp')
