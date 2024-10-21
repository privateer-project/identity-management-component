import os

HOLDER_IP_ADDRESS = os.environ.get("HOLDER_IP")
HOLDER_ADMIN_PORT = os.environ.get("HOLDER_ADMIN_PORT")
ALIAS = os.environ.get("LABEL")
TYPE = os.environ.get("TYPE")
ISSUER_FastAPI_IP_ADDRESS = os.environ.get("ISSUER_IP")
ISSUER_FastAPI_PORT = os.environ.get("ISSUER_PORT")
VERIFIER_FastAPI_IP_ADDRESS = os.environ.get("VERIFIER_IP")
VERIFIER_FastAPI_PORT = os.environ.get("VERIFIER_PORT")
LEDGER_IP_ADDRESS = os.environ.get("LEDGER_IP")
LEDGER_PORT = os.environ.get("LEDGER_PORT")
HOLDER_BASE_URL = "http://" + HOLDER_IP_ADDRESS + ":" + HOLDER_ADMIN_PORT
ISSUER_FastAPI_BASE_URL = "http://" + ISSUER_FastAPI_IP_ADDRESS + ":" + ISSUER_FastAPI_PORT
VERIFIER_FastAPI_BASE_URL = "http://" + VERIFIER_FastAPI_IP_ADDRESS + ":" + VERIFIER_FastAPI_PORT
LEDGER_BASE_URL = "http://" + LEDGER_IP_ADDRESS + ":" + LEDGER_PORT
