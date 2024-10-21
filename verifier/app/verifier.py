import aiohttp
import asyncio
import calendar
import datetime
import json
import re
import time

from config import ALIAS, ISSUER_FastAPI_BASE_URL, LEDGER_BASE_URL, VERIFIER_BASE_URL

async def create_did():

    async with aiohttp.ClientSession() as session:

        url = VERIFIER_BASE_URL + "/wallet/did/create"

        did = ""
        verkey = ""

        async with session.post(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                #print(json.dumps(response, indent=2))
                if "result" in response and response["result"] != None and "did" in response["result"] and "verkey" in response["result"]:
                    did = response["result"]["did"]
                    verkey = response["result"]["verkey"]
        return did, verkey


async def register_did(did, verkey):

    async with aiohttp.ClientSession() as session:

        url = LEDGER_BASE_URL + "/register"

        data = {}
        data["did"] = did
        data["verkey"] = verkey
        data["alias"] = ALIAS

        async with session.post(url, json=data) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                #print(json.dumps(response, indent=2))
                if "did" in response:
                    did = response["did"]
        return did


async def publish_did(did):

    async with aiohttp.ClientSession() as session:

        url = VERIFIER_BASE_URL + "/wallet/did/public"

        parameters = {"did": did}

        async with session.post(url, params=parameters) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                #print(json.dumps(response, indent=2))
            else:
                response = await response.text()
                #print(response)


async def get_public_did():

    async with aiohttp.ClientSession() as session:

        url = VERIFIER_BASE_URL + "/wallet/did/public"

        did = ""

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                if "result" in response and response["result"] != None and "did" in response["result"]:
                    did = response["result"]["did"]
            return did


async def get_private_did():

    async with aiohttp.ClientSession() as session:

        url = VERIFIER_BASE_URL + "/wallet/did"

        did = ""

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                if response["results"]:
                    for record in response["results"]:
                        if "did" in record:
                            did = record["did"]
                            break
            return did


async def get_connections():

    async with aiohttp.ClientSession() as session:

        url = VERIFIER_BASE_URL + "/connections"

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                #print(json.dumps(response, indent=2))


async def get_active_connection(their_label):

    async with aiohttp.ClientSession() as session:

        url = VERIFIER_BASE_URL + "/connections"

        parameters = {"state": "active", "their_label": their_label}

        connection_id = ""

        async with session.get(url, params=parameters) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                if response["results"]:
                    connection = max(response["results"], key=lambda u: u["updated_at"])
                    connection_id = connection["connection_id"]
        return connection_id


async def get_schema_id_by_type(h_type):

    async with aiohttp.ClientSession() as session:
        
        url = ISSUER_FastAPI_BASE_URL + "/get-schema-id/" + h_type

        schema_id = ""
        
        async with session.get(url) as response:
            schema_id = await response.json()
            return schema_id


async def get_attributes_by_type(h_type):

    async with aiohttp.ClientSession() as session:
        
        url = ISSUER_FastAPI_BASE_URL + "/get-attributes/" + h_type

        schema_attributes = []
        
        async with session.get(url) as response:
            schema_attributes = await response.json()
            return schema_attributes


def set_validity_period():

    date_time = datetime.datetime.now() + datetime.timedelta(hours=24) #TODO Change validity period.
    date = calendar.timegm(date_time.timetuple())

    return date


async def send_proof_request(presentation):

    async with aiohttp.ClientSession() as session:

        url = VERIFIER_BASE_URL + "/present-proof-2.0/send-request"

        pres_ex_id = ""

        async with session.post(url, json=presentation) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                #print(json.dumps(response, indent=2))
                if "pres_ex_id" in response:
                    pres_ex_id = response["pres_ex_id"]
        return pres_ex_id


async def verify_presentation(pres_ex_id):

    async with aiohttp.ClientSession() as session:

        url = VERIFIER_BASE_URL + "/present-proof-2.0/records/" + pres_ex_id

        state = ""
        verified = ""

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                #print(json.dumps(response, indent=2))
                if "state" in response:
                    state = response["state"]
                    if "verified" in response:
                        verified = response["verified"]
        return state, verified


async def resolve_did(did):

    async with aiohttp.ClientSession() as session:

        url = VERIFIER_BASE_URL + "/resolver/resolve/did:sov:" + did
        
        did_document = {}

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                #print(json.dumps(response, indent=2))
                if "did_document" in response:
                    did_document = response["did_document"]
            else:
                response = await response.text()
                #print(response)
            return did_document


def validate_did(did):

    prefix = "did:sov:"

    if did != None and did != "":
        if did.startswith(prefix):
            did = did[len(prefix):]

        #re.match("^[1-9A-HJ-NP-Za-km-z]{21,22}$", did):
        if re.match("^[A-Za-z0-9]{21,22}$", did):
            did_is_valid = True
        else:
            did_is_valid = False
    else:
        did_is_valid = False
    
    return did_is_valid, did