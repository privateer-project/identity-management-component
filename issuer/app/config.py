import os

ISSUER_IP_ADDRESS = os.environ.get("ISSUER_IP")
ISSUER_ADMIN_PORT = os.environ.get("ISSUER_ADMIN_PORT")
ALIAS = os.environ.get("LABEL")
ISSUER_FastAPI_PORT = os.environ.get("ISSUER_FastAPI_PORT")
LEDGER_IP_ADDRESS = os.environ.get("LEDGER_IP")
LEDGER_PORT = os.environ.get("LEDGER_PORT")
ISSUER_BASE_URL = "http://" + ISSUER_IP_ADDRESS + ":" + ISSUER_ADMIN_PORT
ISSUER_FastAPI_BASE_URL = "http://" + ISSUER_IP_ADDRESS + ":" + ISSUER_FastAPI_PORT
LEDGER_BASE_URL = "http://" + LEDGER_IP_ADDRESS + ":" + LEDGER_PORT
