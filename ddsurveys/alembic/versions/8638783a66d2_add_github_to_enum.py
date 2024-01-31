from sqlalchemy import Enum, Column, String, ForeignKey
from alembic import op

# revision identifiers, used by Alembic.
revision = '8638783a66d2'
down_revision = '30fd4d9401eb'
branch_labels = None
depends_on = None

# Define old and new enums
old_enum = ['fitbit', 'instagram']
new_enum = ['fitbit', 'instagram', 'github']

old_type = Enum(*old_enum, name='dataprovidertype')
new_type = Enum(*new_enum, name='dataprovidertype_new')


def upgrade() -> None:
    # Create new type
    new_type.create(op.get_bind())

    # 1. Drop the Foreign Key Constraints
    op.drop_constraint('data_connection_ibfk_2', 'data_connection', type_='foreignkey')
    op.drop_constraint('data_provider_access_ibfk_1', 'data_provider_access', type_='foreignkey')

    # 2. Update the Enum in DataProvider:
    op.add_column('data_provider', Column('temp_enum', new_type))
    op.execute('UPDATE data_provider SET temp_enum=data_provider_type')
    op.drop_column('data_provider', 'data_provider_type')
    op.alter_column('data_provider', 'temp_enum', new_column_name='data_provider_type', existing_type=new_type)

    # 3. Update the Enum in DataConnection:
    op.add_column('data_connection', Column('temp_enum', new_type))
    op.execute('UPDATE data_connection SET temp_enum=data_provider_type')
    op.drop_column('data_connection', 'data_provider_type')
    op.alter_column('data_connection', 'temp_enum', new_column_name='data_provider_type', existing_type=new_type)

    # 4. Update the Enum in DataProviderAccess:
    op.add_column('data_provider_access', Column('temp_enum', new_type))
    op.execute('UPDATE data_provider_access SET temp_enum=data_provider_type')
    op.drop_column('data_provider_access', 'data_provider_type')
    op.alter_column('data_provider_access', 'temp_enum', new_column_name='data_provider_type', existing_type=new_type)

    # 5. Re-create the Foreign Key Constraints
    op.create_foreign_key('data_connection_ibfk_2', 'data_connection', 'data_provider', ['data_provider_type'], ['data_provider_type'])
    op.create_foreign_key('data_provider_access_ibfk_1', 'data_provider_access', 'data_provider', ['data_provider_type'], ['data_provider_type'])

    # Drop old enum type
    old_type.drop(op.get_bind(), checkfirst=False)


def downgrade() -> None:
    # Similar steps in reverse order
    pass  # It's generally trickier to safely downgrade enum changes. Depending on your use case, you may choose to not support downgrades, or you might revert the change similar to the upgrade path.
