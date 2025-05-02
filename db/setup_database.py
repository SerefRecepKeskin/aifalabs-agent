from .connector import get_connection
from util import logger
from sqlalchemy import Column, DateTime, Integer, VARCHAR, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

# Define initial setup function
async def setup_database():
    """Create necessary tables if they don't exist"""
    logger.info("Starting database setup process")
    try:
        async with get_connection() as conn:
            logger.info("Creating products table if it doesn't exist")
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            logger.info("Products table setup complete")
            
            # Create chat_history table
            logger.info("Creating chat_history table if it doesn't exist")
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    session_id VARCHAR(255) NOT NULL,
                    messages JSONB NOT NULL DEFAULT '[]'::jsonb,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT uix_session_user UNIQUE (session_id, user_id)
                )
            ''')
            logger.info("Chat history table setup complete")
            
            # Create indexes for chat_history
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history (user_id);
                CREATE INDEX IF NOT EXISTS idx_chat_history_session_id ON chat_history (session_id);
            ''')
            logger.info("Chat history indexes created")
            
            # Check if we need to add sample data to products
            row_count = await conn.fetchval('SELECT COUNT(*) FROM products')
            if row_count == 0:
                # Add some sample products
                logger.info("Adding sample product data")
                await conn.executemany(
                    '''
                    INSERT INTO products (name, description, price)
                    VALUES ($1, $2, $3)
                    ''',
                    [
                        ('Smartphone X', 'Latest smartphone with 5G capabilities and 48MP camera', 799.99),
                        ('Laptop Pro', 'High performance laptop for professionals with 16GB RAM', 1299.99),
                        ('Wireless Earbuds', 'Premium wireless earbuds with noise cancellation', 149.99),
                        ('Smart Watch', 'Fitness tracker with heart rate monitoring', 199.99),
                        ('Coffee Maker', 'Programmable coffee maker with thermal carafe', 129.99),
                    ]
                )
                logger.info(f"Added 5 sample products to the database")
            else:
                logger.info(f"Database already contains {row_count} products, skipping sample data")
            
        logger.info("Database setup completed successfully")
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        raise