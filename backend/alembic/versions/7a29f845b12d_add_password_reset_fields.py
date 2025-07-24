"""add_password_reset_fields

Revision ID: 7a29f845b12d
Revises: 4e68103371c9
Create Date: 2025-01-17 17:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a29f845b12d'
down_revision: Union[str, None] = '4e68103371c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add password reset fields to users table."""
    # Add reset_token column
    op.add_column('users', sa.Column('reset_token', sa.String(length=255), nullable=True, comment='Password reset token (hashed)'))
    
    # Add reset_token_expires column  
    op.add_column('users', sa.Column('reset_token_expires', sa.DateTime(timezone=True), nullable=True, comment='Password reset token expiration time'))
    
    # Create index on reset_token for performance
    op.create_index(op.f('ix_users_reset_token'), 'users', ['reset_token'], unique=False)


def downgrade() -> None:
    """Remove password reset fields from users table."""
    # Drop index first
    op.drop_index(op.f('ix_users_reset_token'), table_name='users')
    
    # Drop columns
    op.drop_column('users', 'reset_token_expires')
    op.drop_column('users', 'reset_token') 