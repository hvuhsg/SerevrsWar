import os
from qwhale_client import APIClient


TOKEN = os.getenv("QWHALE_TOKEN", None)
if not TOKEN:
    raise RuntimeError("Set environment variable QWHALE_TOKEN")
    # set QWHALE_TOKEN=152507d95f73f1630f742f18a213e612:d40c452cd512234cfaef4e5045414561

client = APIClient(TOKEN)
db = None


def setup_db():
    global db
    db = client.get_database()


def shutdown_db():
    client.close()


def get_db():
    global db
    return db
