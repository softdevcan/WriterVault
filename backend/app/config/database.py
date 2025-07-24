"""
Modern SQLAlchemy 2.0+ Database Configuration.
Uses DeclarativeBase, sessionmaker, and dependency injection patterns.
"""
import logging
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.pool import NullPool

from app.config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """
    Modern SQLAlchemy 2.0+ Declarative Base.
    All ORM models will inherit from this base class.
    """
    pass


# Create SQLAlchemy engine with modern configuration
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True,  # Enable SQLAlchemy 2.0+ mode
    # Connection pool settings
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections every hour
    # For PostgreSQL optimization
    connect_args={
        "options": "-c timezone=utc"  # Set timezone to UTC
    } if settings.DATABASE_URL.startswith("postgresql") else {}
)

# Modern sessionmaker factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False  # Keep objects accessible after commit
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection function for database sessions.
    
    Usage in FastAPI endpoints:
        async def endpoint(db: Session = Depends(get_db)):
            # Use db session
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        logger.debug("🔗 Database session created")
        yield db
    except Exception as e:
        logger.error(f"🚨 Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        logger.debug("🔒 Database session closed")
        db.close()


def create_tables():
    """
    Create all database tables.
    
    This function creates all tables defined in the Base.metadata.
    Should be called during application startup.
    """
    try:
        logger.info("📊 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"🚨 Failed to create database tables: {str(e)}")
        raise


def drop_tables():
    """
    Drop all database tables.
    
    WARNING: This will delete all data!
    Only use for development/testing.
    """
    try:
        logger.warning("🗑️ Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.warning("✅ All database tables dropped")
    except Exception as e:
        logger.error(f"🚨 Failed to drop database tables: {str(e)}")
        raise


# Database event listeners for logging
@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    """Log database connections."""
    logger.info("🔌 New database connection established")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout from pool."""
    logger.debug("📤 Database connection checked out from pool")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log connection checkin to pool."""
    logger.debug("📥 Database connection checked in to pool") 