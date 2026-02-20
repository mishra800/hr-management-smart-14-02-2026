# PostgreSQL Database Connection Module
import os
import logging
from typing import Generator
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# Load environment variables from root .env file
# Try multiple paths to find .env file (prioritize root .env)
env_paths = [
    Path.cwd() / '.env',  # workspace_root/.env (PRIORITY)
    Path(__file__).parent.parent.parent / '.env',  # root/.env (from backend/app/)
    Path(__file__).parent.parent / '.env',  # backend/.env (fallback)
    Path.cwd() / 'backend' / '.env',  # workspace_root/backend/.env (fallback)
]

env_loaded = False
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        env_loaded = True
        logger.info(f"✓ Loaded environment variables from: {env_path}")
        break

if not env_loaded:
    load_dotenv()  # Try default behavior
    logger.warning("⚠ Using default .env loading behavior")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment (REQUIRED - no default with credentials)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable is not set!")
    logger.error("Please set DATABASE_URL in your .env file")
    logger.error("Example: DATABASE_URL=postgresql://user:password@host:port/database")
    raise ValueError("DATABASE_URL environment variable is required")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Disable connection pooling for simplicity
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,  # Enable connection health checks
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


# Dependency to get database session
def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_db_connection() -> bool:
    """Test database connection"""
    try:
        # Try to connect to the database
        with engine.connect() as connection:
            from sqlalchemy import text
            result = connection.execute(text("SELECT 1"))
            logger.info("✓ Database connection successful!")
            logger.info(f"✓ Connected to: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'database'}")
            return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        logger.error(f"✗ Connection string: {DATABASE_URL.replace(DATABASE_URL.split(':')[2].split('@')[0], '***') if ':' in DATABASE_URL else DATABASE_URL}")
        return False


def init_db():
    """Initialize database - create all tables"""
    try:
        # Import all models here to ensure they're registered with Base
        # This imports the consolidated models.py with all SQLAlchemy ORM models
        from app import models  # noqa: F401
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to create database tables: {e}")
        return False


# Database session context manager
class DatabaseSession:
    """Context manager for database sessions"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def __enter__(self) -> Session:
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error(f"Database session error: {exc_val}")
            self.db.rollback()
        self.db.close()
        return False


def get_db_session():
    """Get database session context manager"""
    return DatabaseSession()

