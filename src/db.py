import os
from qwhale_client import APIClient


TOKEN = os.getenv("QWHALE_TOKEN", None)
if not TOKEN:
    raise RuntimeError("Set environment variable QWHALE_TOKEN")

client = APIClient(TOKEN)
db = None


def setup_db():
    global db
    db = client.get_database()


def shutdown_db():
    try:
        db.close()
    finally:
        client.close()


def get_db():
    global db
    return db
