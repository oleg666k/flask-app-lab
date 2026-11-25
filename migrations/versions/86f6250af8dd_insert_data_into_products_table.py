"""Insert data into products table

Revision ID: 86f6250af8dd
Revises: 0d209b637d54
Create Date: 2026-11-25 17:55:42.154588

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = '86f6250af8dd'
down_revision = '0d209b637d54'
branch_labels = None
depends_on = None


def upgrade():

    categories_table = table(
        'categories',
        column('id', sa.Integer),
        column('name', sa.String)
    )

    products_table = table(
        'products',
        column('name', sa.String),
        column('price', sa.Float),
        column('active', sa.Boolean),
        column('category_id', sa.Integer)
    )

    op.bulk_insert(categories_table, [
        {'name': 'Electronics'},
        {'name': 'Books'},
        {'name': 'Clothing'}
    ])

    connection = op.get_bind()

    result = connection.execute(
        sa.select(
            categories_table.c.name,
            categories_table.c.id
        )
    )

    category_ids = dict(result.all())

    op.bulk_insert(products_table, [
        {
            'name': 'Laptop',
            'price': 1200.0,
            'active': True,
            'category_id': category_ids['Electronics']
        },
        {
            'name': 'Smartphone LG',
            'price': 800.0,
            'active': True,
            'category_id': category_ids['Electronics']
        },
        {
            'name': 'Novel',
            'price': 20.0,
            'active': True,
            'category_id': category_ids['Books']
        },
        {
            'name': 'T-Shirt',
            'price': 25.0,
            'active': False,
            'category_id': category_ids['Clothing']
        }
    ])


def downgrade():

    op.execute("""
        DELETE FROM products
        WHERE name IN (
            'Laptop',
            'Smartphone LG',
            'Novel',
            'T-Shirt'
        )
        AND category_id IN (
            SELECT id FROM categories
            WHERE name IN (
                'Electronics',
                'Books',
                'Clothing'
            )
        );
    """)

    op.execute("""
        DELETE FROM categories
        WHERE name IN (
            'Electronics',
            'Books',
            'Clothing'
        );
    """)