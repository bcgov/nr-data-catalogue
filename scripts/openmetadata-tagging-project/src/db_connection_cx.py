# Filename: db_connection_cx.py
from sqlalchemy import create_engine
from dotenv import load_dotenv, dotenv_values
import os
import logging

def get_db_connection():
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Load environment variables
    load_dotenv()
    env_vars = dotenv_values()

    # Mask password for logging
    def mask_password(password):
        return '*' * len(password) if password else None

    # Log environment variables (except password)
    logging.info(f"ORACLE_DRIVER: {env_vars.get('ORACLE_DRIVER')}")
    logging.info(f"ORACLE_DSN: {env_vars.get('ORACLE_DSN')}")
    logging.info(f"ORACLE_USER: {env_vars.get('ORACLE_USER')}")
    logging.info(f"ORACLE_PASSWORD: {mask_password(env_vars.get('ORACLE_PASSWORD'))}")
    logging.info(f"TNS_ADMIN: {env_vars.get('TNS_ADMIN')}")

    # Construct the SQLAlchemy connection string
    connection_string = (
        f"oracle+cx_oracle://{env_vars.get('ORACLE_USER')}:{env_vars.get('ORACLE_PASSWORD')}@"
        f"{env_vars.get('ORACLE_DSN')}"
    )

    try:
        # Use SQLAlchemy to create an engine (connection)
        engine = create_engine(connection_string)
        logging.info("Connection successful!")
        return engine
    except Exception as e:
        logging.error(f"Connection failed: {str(e)}")
        raise
