import aiohttp
import asyncio
import datetime
import json
import random
import re
import time

from config import ALIAS, ISSUER_BASE_URL, ISSUER_FastAPI_BASE_URL, LEDGER_BASE_URL

async def create_did():

    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/wallet/did/create"

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

        url = ISSUER_BASE_URL + "/wallet/did/public"

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

        url = ISSUER_BASE_URL + "/wallet/did/public"

        did = ""

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                if "result" in response and response["result"] != None and "did" in response["result"]:
                    did = response["result"]["did"]
            return did


#TODO Declare attributes and schema_name properly! Declare if each schema supports revocation!
def declare_schema_info():

    schema = {}

    schema_info = {}
    attributes = ["mno1", "mno2"]
    support_revocation = True
    schema_info["schema_name"] = "mno schema"
    schema_info["attributes"] = attributes
    schema_info["support_revocation"] = support_revocation
    schema["mno"] = schema_info

    schema_info = {}
    attributes = ["sp1"]
    support_revocation = True
    schema_info["schema_name"] = "sp schema"
    schema_info["attributes"] = attributes
    schema_info["support_revocation"] = support_revocation
    schema["sp"] = schema_info

    schema_info = {}
    attributes = ["user1"]
    support_revocation = True
    schema_info["schema_name"] = "user schema"
    schema_info["attributes"] = attributes
    schema_info["support_revocation"] = support_revocation
    schema["user"] = schema_info

    #print(json.dumps(schema, indent=2))
    return schema


async def create_schema(schema_name, attributes):
    #If schema_name already exists, change schema_version!
    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/schemas"

        schema = {}
        schema["schema_name"] = schema_name.replace(" ", "_" )
        schema["schema_version"] = "1.0"
        schema["attributes"] = attributes

        schema_id = ""

        async with session.post(url, json=schema) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                if "sent" in response and "schema_id" in response["sent"]:
                    schema_id = response["sent"]["schema_id"]
        return schema_id

'''
async def get_schema(schema_id): # Not in use.

    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/schemas/" + schema_id

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                return response
'''

async def get_schemas():

    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/schemas/created"
        
        schema_ids = []

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                if "schema_ids" in response:
                    schema_ids = response["schema_ids"]
                return schema_ids


async def get_schema_attributes(schema_id):

    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/schemas/" + schema_id
        
        attributes = []

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                if "schema" in response and "attrNames" in response["schema"]:
                    attributes = response["schema"]["attrNames"]
                return attributes


async def get_schema_id(h_type):
    
    schema_ids = []
    schema_id = ""
    schema_ids = await get_schemas()

    for s_id in schema_ids:
        if h_type.lower() in s_id:
            schema_id = s_id
            break

    return schema_id

        
async def create_credential_definition(schema_id, support_revocation):

    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/credential-definitions"

        schema_id_segments = re.split(":", schema_id)

        credential_definition = {}
        credential_definition["support_revocation"] = support_revocation
        credential_definition["tag"] = schema_id_segments[2].replace(" ", "_" ) + "_v" + schema_id_segments[3] #Optional
        credential_definition["schema_id"] = schema_id
        if credential_definition["support_revocation"] == True:
            credential_definition["revocation_registry_size"] = 32768 #Value must be an integer between 4 and 32768 inclusively. Declare it only in case of revocation.

        credential_definition_id = ""

        async with session.post(url, json=credential_definition) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                if "sent" in response and "credential_definition_id" in response["sent"]:
                    credential_definition_id = response["sent"]["credential_definition_id"]
        return credential_definition_id

'''
async def get_credential_definitions(): # Not in use.

    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/credential-definitions/created"

        cred_def_ids = []

        async with session.get(url) as response:
            response = await response.json()
            cred_def_ids = response["credential_definition_ids"]
            return cred_def_ids
'''

async def get_credential_definition(schema_id):

    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/credential-definitions/created"

        parameters = {'schema_id': schema_id}
        cred_def_id = ""

        async with session.get(url, params=parameters) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                if "credential_definition_ids" in response and response["credential_definition_ids"]:
                    cred_def_id = response["credential_definition_ids"][0]
            return cred_def_id


async def support_revocation(cred_def_id):

    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/revocation/active-registry/" + cred_def_id

        revocation = False

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                if "result" in response and response["result"] != None and "state" in response["result"] and response["result"]["state"] == "active":
                    revocation = True
            return revocation


async def get_connections():

    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/connections"

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                #print(json.dumps(response, indent=2))


async def get_active_registry(cred_def_id):

    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/revocation/active-registry/" + cred_def_id

        revoc_reg_id = ""

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                if "result" in response and "revoc_reg_id" in response["result"]:
                    revoc_reg_id = response["result"]["revoc_reg_id"]
            return revoc_reg_id


async def create_credential(attributes_values, schema_id, cred_def_id, revocation, connection_id):
    
    credential = {}

    issuer_did = await get_public_did()

    schema_id_segments = re.split(":", schema_id)

    schema_version = schema_id_segments[3]
    schema_issuer_did = issuer_did
    schema_name = schema_id_segments[2]

    filter = {}
    credential_preview = {}
    indy = {}

    if revocation is True:
        credential["revoc_reg_id"] = await get_active_registry(cred_def_id)
        credential["auto_remove"] = False
    else:
        credential["auto_remove"] = True

    credential["connection_id"] = connection_id

    credential_preview["@type"] = "issue-credential-2.0/credential-preview"
    credential_preview["attributes"] = attributes_values

    credential["credential_preview"] = credential_preview

    indy["cred_def_id"] = cred_def_id
    indy["issuer_did"] = issuer_did
    indy["schema_id"] = schema_id
    indy["schema_issuer_did"] = schema_issuer_did
    indy["schema_name"] = schema_name
    indy["schema_version"] = schema_version

    filter["indy"] = indy

    credential["filter"] = filter
    credential["trace"] = False

    #print(json.dumps(credential, indent=2))

    return credential


async def get_credential_records():

    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/issue-credential-2.0/records"

        credentials = []

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                if "results" in response:
                    credentials = response["results"]
                    #print(json.dumps(credentials, indent=2))
            return credentials

'''
def credential_already_exists(issued_credentials, new_credential): # Not in use.

    active_credential_exists = False
    new_credential_attributes_values = new_credential["credential_preview"]["attributes"]

    for credential in issued_credentials:
        i = 0

        if "cred_ex_record" in credential and "by_format" in credential["cred_ex_record"] and "cred_issue" in credential["cred_ex_record"]["by_format"] and "indy" in credential["cred_ex_record"]["by_format"]["cred_issue"] and "schema_id" in credential["cred_ex_record"]["by_format"]["cred_issue"]["indy"]:
            schema_id = credential["cred_ex_record"]["by_format"]["cred_issue"]["indy"]["schema_id"]
            if schema_id == new_credential["filter"]["indy"]["schema_id"]:
                if "cred_ex_record" in credential and "state" in credential["cred_ex_record"] and credential["cred_ex_record"]["state"] == "done":
                    if "cred_ex_record" in credential and "by_format" in credential["cred_ex_record"] and "cred_issue" in credential["cred_ex_record"]["by_format"] and "indy" in credential["cred_ex_record"]["by_format"]["cred_issue"] and "values" in credential["cred_ex_record"]["by_format"]["cred_issue"]["indy"]:
                        values = {}
                        values = credential["cred_ex_record"]["by_format"]["cred_issue"]["indy"]["values"]
                        issue_credential_attributes = []
                        for key in values:
                            issue_credential_attributes.append(key)
                        for record in new_credential_attributes_values:
                            new_credential_attribute = new_credential_attributes_values["name"]
                            new_credential_value = new_credential_attributes_values["value"]
                            if new_credential_attribute in issue_credential_attributes and "raw" in values[new_credential_attribute] and new_credential_value == values[new_credential_attribute]["raw"]:
                                i+=1
                                
        if i == len(new_credential_attributes_values):
            active_credential_exists = True
            break

    return active_credential_exists
'''

async def issue_credential(credential):

    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/issue-credential-2.0/send"

        async with session.post(url, json=credential) as response:
            status = response.status
            if status == 200:
                credential_issued = True
                response = await response.json()
            else:
                credential_issued = False
        return credential_issued


async def get_issued_credentials():

    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/issue-credential-2.0/records"

        counter = 0
        rev_reg_id = ""
        cred_rev_id = -1
        cred_ids = {}

        async with session.get(url) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                for credential in response["results"]:
                    if "cred_ex_record" in credential and "state" in credential["cred_ex_record"] and credential["cred_ex_record"]["state"] == "done":
                        if "connection_id" in credential["cred_ex_record"] and "thread_id" in credential["cred_ex_record"] and "cred_ex_id" in credential["cred_ex_record"] and "indy" in credential and "cred_rev_id" in credential["indy"]:
                            if "by_format" in credential["cred_ex_record"] and "cred_issue" in credential["cred_ex_record"]["by_format"] and "indy" in credential["cred_ex_record"]["by_format"]["cred_issue"] and "rev_reg_id" in credential["cred_ex_record"]["by_format"]["cred_issue"]["indy"]:
                                counter += 1
                                
                                rev_reg_id = credential["cred_ex_record"]["by_format"]["cred_issue"]["indy"]["rev_reg_id"]
                                cred_rev_id = credential["indy"]["cred_rev_id"]
                                connection_id = credential["cred_ex_record"]["connection_id"]        
                                thread_id = credential["cred_ex_record"]["thread_id"]
                                cred_ex_id = credential["cred_ex_record"]["cred_ex_id"]

                                credential_ids = {}
                                credential_ids["rev_reg_id"] = rev_reg_id
                                credential_ids["cred_rev_id"] = cred_rev_id
                                credential_ids["connection_id"] = connection_id
                                credential_ids["thread_id"] = thread_id
                                credential_ids["cred_ex_id"] = cred_ex_id
                                cred_ids[counter] = credential_ids
        return cred_ids


def integer_within_range(array):

    index = input("Select a credential by id, e.g. 1. Input: ")

    while True:
        if index.strip().isdigit():
            index = int(index)
            if (index >= 1 and index <= len(array)):
                break
            else:
                index = input("Select a credential by id, e.g. 1. Input: ")
        else:
            index = input("Select a credential by id, e.g. 1. Input: ")
    
    return index


async def revoke_credential(rev_reg_id, cred_rev_id, connection_id, thread_id):

    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/revocation/revoke"

        data = {}
        data["rev_reg_id"] = rev_reg_id
        data["cred_rev_id"] = cred_rev_id
        data["publish"] = True
        data["notify"] = True # True|False
        data["connection_id"] = connection_id
        data["thread_id"] = thread_id

        message = ""

        async with session.post(url, json=data) as response:
            status = response.status            
            if status == 200:
                message = "Credential revoked successfully!"
            else:
                message = "An error occured during credential revocation!"
            response = {}
            response["status"] = status
            response["message"] = message
            return response


async def delete_credential(cred_ex_id):

    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/issue-credential-2.0/records/" + cred_ex_id

        message = ""

        async with session.delete(url) as response:
            status = response.status
            if status == 200:
                message = "Revoked credential deleted successfully!"
            else:
                message = "An error occured when deleting credential!"
            response = {}
            response["status"] = status
            response["message"] = message
            return response


async def resolve_did(did):

    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/resolver/resolve/did:sov:" + did

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