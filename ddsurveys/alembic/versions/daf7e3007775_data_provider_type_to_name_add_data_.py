"""data provider type to name, adjust data provider type.

Revision ID: daf7e3007775
Revises: 991bc07484f8
Create Date: 2024-03-14 15:01:41.091442

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "daf7e3007775"
down_revision = "991bc07484f8"
branch_labels = None
depends_on = None

# Assuming the Enums are defined elsewhere and imported here
# Adjust these enums or create them as needed for your database


def upgrade():

    # remove foreign keys contraints from data_connection and data_provider_access to data_provider column data_provider_type
    op.drop_constraint("data_connection_ibfk_1", "data_connection", type_="foreignkey")
    op.drop_constraint("data_connection_ibfk_2", "data_connection", type_="foreignkey")
    op.drop_constraint(
        "data_provider_access_ibfk_1", "data_provider_access", type_="foreignkey"
    )
    op.drop_constraint(
        "data_provider_access_ibfk_2", "data_provider_access", type_="foreignkey"
    )
    op.drop_constraint(
        "data_provider_access_ibfk_3", "data_provider_access", type_="foreignkey"
    )

    op.drop_constraint("data_connection_pkey", "data_connection", type_="primary")
    op.drop_constraint(
        "data_provider_access_pkey", "data_provider_access", type_="primary"
    )
    # disable primary key constraint on data_provider table, the key was data_provider_type and now its data_provider_name
    op.drop_constraint("data_provider_pkey", "data_provider", type_="primary")

    # Step 2: Add 'data_provider_name' column
    op.add_column(
        "data_provider",
        sa.Column(
            "data_provider_name",
            sa.Enum(
                "Fitbit",
                "Instagram",
                "GitHub",
                "DDS",
                "GoogleContacts",
                name="dataprovidername",
            ),
            nullable=False,
        ),
    )
    op.execute("UPDATE data_provider SET data_provider_name = data_provider_type")

    op.add_column(
        "data_connection",
        sa.Column(
            "data_provider_name",
            sa.Enum("Fitbit", "Instagram", "GitHub", "DDS", "GoogleContacts", name="dataprovidername"),
            nullable=False,
        ),
    )
    op.execute("UPDATE data_connection SET data_provider_name = data_provider_type")

    op.add_column(
        "data_provider_access",
        sa.Column(
            "data_provider_name",
            sa.Enum("Fitbit", "Instagram", "GitHub", "DDS", "GoogleContacts", name="dataprovidername"),
            nullable=False,
        ),
    )
    op.execute(
        "UPDATE data_provider_access SET data_provider_name = data_provider_type"
    )

    # Step 3: Revert 'data_provider_type' to a VARCHAR
    op.alter_column(
        "data_provider",
        "data_provider_type",
        type_=sa.String(length=255),
        existing_nullable=True,
    )
    op.alter_column(
        "data_connection",
        "data_provider_type",
        type_=sa.String(length=255),
        existing_nullable=True,
    )
    op.alter_column(
        "data_provider_access",
        "data_provider_type",
        type_=sa.String(length=255),
        existing_nullable=True,
    )

    # Step 4: Set all data_provider_type values to 'oauth'
    op.execute("UPDATE data_provider SET data_provider_type = 'oauth'")
    op.execute("UPDATE data_connection SET data_provider_type = 'oauth'")
    op.execute("UPDATE data_provider_access SET data_provider_type = 'oauth'")

    # Step 5: Set columns to the enum type
    op.alter_column(
        "data_provider",
        "data_provider_name",
        type_=sa.Enum("Fitbit", "Instagram", "GitHub", "DDS", "GoogleContacts", name="dataprovidertype"),
        existing_nullable=True,
    )
    op.alter_column(
        "data_connection",
        "data_provider_type",
        type_=sa.Enum("generic", "oauth", "frontend", name="dataprovidertype"),
        existing_nullable=True,
    )
    op.alter_column(
        "data_provider_access",
        "data_provider_type",
        type_=sa.Enum("generic", "oauth", "frontend", name="dataprovidertype"),
        existing_nullable=True,
    )

    # Step 5: Set data_provider_name as the primary key
    op.create_primary_key("data_provider_pkey", "data_provider", ["data_provider_name"])

    # Step 7: Add composed primary key constraints back to project_id, data_provider_name in data_connection and data_provider_access
    op.create_primary_key(
        "data_connection_pkey", "data_connection", ["project_id", "data_provider_name"]
    )
    op.create_primary_key(
        "data_provider_access_pkey",
        "data_provider_access",
        ["user_id", "project_id", "respondent_id"],
    )

    # Add foreign key constraint to 'data_connection' referencing 'data_provider_name'
    op.create_foreign_key(
        "data_connection_ibfk_1",
        "data_connection",
        "data_provider",
        ["data_provider_name"],
        ["data_provider_name"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "data_connection_ibfk_2",
        "data_connection",
        "project",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Add foreign key constraint to 'data_provider_access' referencing 'data_provider_name'
    op.create_foreign_key(
        "data_provider_access_ibfk_1",
        "data_provider_access",
        "data_provider",
        ["data_provider_name"],
        ["data_provider_name"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "data_provider_access_ibfk_2",
        "data_provider_access",
        "project",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "data_provider_access_ibfk_3",
        "data_provider_access",
        "respondent",
        ["respondent_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
