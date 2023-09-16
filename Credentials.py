import psycopg2
import os
from dotenv import load_dotenv


# Securely assign credentials from env file
def getCredentials():
    """
    Get credentials for connecting to PostgreSQL database.

    :return: PostgreSQL connection object.
    :rtype: psycopg2.extensions.connection
    """
    load_dotenv('.env')
    conn = psycopg2.connect(
        host=os.getenv('host'),
        port=os.getenv('port'),
        database=os.getenv('database'),
        user=os.getenv('user'),
        password=os.getenv('password')
    )
    return conn
