import asyncpg
from contextlib import asynccontextmanager
from config import config
from util.logger import logger

# Database connection parameters from config
DB_HOST = config.postgres.db_host
DB_PORT = config.postgres.db_port
DB_NAME = config.postgres.db_name
DB_USER = config.postgres.db_user
DB_PASSWORD = config.postgres.db_password

# Connection string
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


async def get_connection_pool():
    """Get a connection pool to the database"""
    return await asyncpg.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        min_size=5,
        max_size=20
    )


# Global connection pool
pool = None


@asynccontextmanager
async def get_connection():
    """Get a database connection from the pool."""
    global pool
    if pool is None:
        pool = await get_connection_pool()
    
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)



