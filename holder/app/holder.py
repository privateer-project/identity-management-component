import aiohttp
import asyncio
import json
import re

from config import ALIAS, HOLDER_BASE_URL, ISSUER_FastAPI_BASE_URL, LEDGER_BASE_URL, TYPE, VERIFIER_FastAPI_BASE_URL

async def create_did():

    async with aiohttp.ClientSession() as session:

        url = HOLDER_BASE_URL + "/wallet/did/create"

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

        url = HOLDER_BASE_URL + "/wallet/did/public"

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

        url = HOLDER_BASE_URL + "/wallet/did/public"

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

        url = HOLDER_BASE_URL + "/wallet/did"

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


async def request_invitation(BASE_URL):

    async with aiohttp.ClientSession() as session:

        url = BASE_URL + "/request-invitation"

        invitation = {}

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                invitation = await response.json()

        return invitation


async def receive_oob_invitation(invitation, their_label):

    async with aiohttp.ClientSession() as session:

        url = HOLDER_BASE_URL + "/out-of-band/receive-invitation"

        sender = their_label
        connection_id = ""

        async with session.post(url, json=invitation) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                #print(json.dumps(response, indent=2))
                if "connection_id" in response:
                    connection_id = response["connection_id"]
        return connection_id


async def get_connections():

    async with aiohttp.ClientSession() as session:

        url = HOLDER_BASE_URL + "/connections"

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                #print(json.dumps(response, indent=2))


async def get_attributes_by_type(h_type):

    async with aiohttp.ClientSession() as session:
        
        url = ISSUER_FastAPI_BASE_URL + "/get-attributes/" + h_type

        schema_attributes = []
        
        async with session.get(url) as response:
            schema_attributes = await response.json()
            return schema_attributes


async def create_credential_proposal(connection_id):

    credential_proposal = {}
    credential_preview = {}
    attributes = []
    filter = {}

    credential_proposal["comment"] = "Issue current credential on behalf of " + TYPE + " " + ALIAS + "."
    if connection_id != "":
        credential_proposal["connection_id"] = connection_id

    credential_preview["@type"] = "issue-credential-2.0/credential-preview"

    schema_attributes = await get_attributes_by_type(TYPE)

    attributes_values = []
    
    for i in range(len(schema_attributes)): 
        attribute_value = {}
        attribute_value["name"] = schema_attributes[i]
        attribute_value["value"] = "test_value" + schema_attributes[i][-1] #TODO Change these fixed values!!!
        attributes_values.append(attribute_value)
       
    credential_preview["attributes"] = attributes_values
    
    credential_proposal["credential_preview"] = credential_preview

    filter["indy"] = {}
    credential_proposal["filter"] = filter

    #print(json.dumps(credential_proposal, indent=2))
    
    return credential_proposal


def get_credential_proposal_info(attributes_values):
    
    credential_attributes = []
    credential_attributes_values = {}

    for record in attributes_values:
        attribute = record["name"]
        credential_attributes.append(attribute)
        value = record["value"]
        credential_attributes_values[attribute] = value
    
    #print(json.dumps(credential_attributes_values, indent=2))
    #print(credential_attributes)
    return credential_attributes, credential_attributes_values


async def get_credential_records():

    async with aiohttp.ClientSession() as session:

        url = HOLDER_BASE_URL + "/issue-credential-2.0/records"

        credential_records = []

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                if "results" in response:
                    credential_records = response["results"]
                    #print(json.dumps(credential_records, indent=2))
            return credential_records


def credential_already_exists(stored_credentials, credential_attributes, credential_attributes_values): # The attributes and values of the credential proposal.

    credential_exists = False
    referent = ""

    for credential in stored_credentials:
        i=0
        if "schema_id" in credential:
            schema_id = credential["schema_id"]
            if "attrs" in credential:
                attrs = {}
                attrs = credential["attrs"]
                for key in attrs: # key = the attribute of the existing credential
                    if key in credential_attributes and key in attrs:
                        attribute_value = credential_attributes_values[key]
                        if attribute_value == attrs[key]:
                            i+=1

        if i == len(credential_attributes):
            if "referent" in credential:
                referent = credential["referent"]
                credential_exists = True
                break

    return credential_exists, referent


async def request_credential(credential_proposal):

    async with aiohttp.ClientSession() as session:

        url = ISSUER_FastAPI_BASE_URL + "/request-credential"

        async with session.post(url, json=credential_proposal) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                #print(json.dumps(response, indent=2))
                return response
            else:
                response = await response.text()
                #print(response)
                return {}


async def get_credential_state_by_id(referent):

    async with aiohttp.ClientSession() as session:

        url = HOLDER_BASE_URL + "/credential/revoked/" + referent

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                #print(json.dumps(response, indent=2))
                if "revoked" in response:
                    revoked = response["revoked"]
                    return revoked


async def delete_revoked_credential(credential_id):

    async with aiohttp.ClientSession() as session:

        url = HOLDER_BASE_URL + "/credential/" + credential_id

        message = ""

        async with session.delete(url) as response:
            status = response.status
            if status == 200:
                message = "Revoked credential deleted successfully!"
            else:
                message = "An error occured when deleting credential!"
            response = {}
            response["status"] = status
            response["response"] = message
            return response


async def get_credentials():

    async with aiohttp.ClientSession() as session:

        url = HOLDER_BASE_URL + "/credentials"

        stored_credentials = []

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                #print(json.dumps(response, indent=2))
                if "results" in response:
                    stored_credentials = response["results"]
                    #print(json.dumps(stored_credentials, indent=2))
            return stored_credentials


async def request_verification():

    async with aiohttp.ClientSession() as session:

        url = VERIFIER_FastAPI_BASE_URL + "/request-verification"
        
        parameters = {"h_type": TYPE, "their_label": ALIAS}
        
        async with session.get(url, params=parameters) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                #print(json.dumps(response, indent=2))
                return response
            else:
                response = await response.text()
                #print(response)
                return {}


async def delete_active_connection(connection_id):

    async with aiohttp.ClientSession() as session:

        url = HOLDER_BASE_URL + "/connections/" + connection_id

        message = ""

        async with session.delete(url) as response:
            status = response.status
            if status == 200:
                message = "Connection deleted successfully!"
            else:
                message = "An error occured when deleting connection!"
            response = {}
            response["status"] = status
            response["message"] = message
            return response


async def resolve_did(did):

    async with aiohttp.ClientSession() as session:

        url = HOLDER_BASE_URL + "/resolver/resolve/did:sov:" + did

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