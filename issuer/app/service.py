import aiohttp
import asyncio
import json
import re
import sys
import uvicorn

from config import ISSUER_BASE_URL, ISSUER_FastAPI_PORT
from fastapi import FastAPI, Request
from issuer import get_schema_attributes, get_schema_id, get_credential_definition, support_revocation, create_credential, issue_credential

app = FastAPI()

@app.get("/request-invitation")
async def request_invitation():
    invitation: json = await create_oob_invitation()

    return invitation


async def create_oob_invitation():

    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/out-of-band/create-invitation"

        data = {}
        data["use_public_did"] = True # True|False
        data["handshake_protocols"] = ["rfc23"]

        invitation = {}

        async with session.post(url, json=data) as response:
            status = response.status
            if status == 200:
                response = await response.json()
                #print(json.dumps(response, indent=2))
                if "invitation" in response:
                    invitation = response["invitation"]
        return invitation


@app.post("/request-credential")
async def request_credential(request: Request):
    credential_proposal: json = await request.json()

    comment = credential_proposal["comment"]
    holder_info = comment.replace("Issue current credential on behalf of ", "").replace(".", "")
    holder_info_segments = re.split(" ", holder_info)
    h_type = holder_info_segments[0]
    their_label = holder_info_segments[1]
    attributes_values = credential_proposal["credential_preview"]["attributes"]

    proposal_accepted, response = await accept_credential_proposal(h_type, their_label, attributes_values)
    response_message = {}

    if proposal_accepted == True:
        credential = response
        if isinstance(credential, dict):
            credential_issued = await issue_credential(credential)
            if credential_issued:
                response_message["status"] = 200
                response_message["response"] = "A new credential was successfully issued!"
            else:
                response_message["status"] = 400
                response_message["response"] = "Could not issue a credential on behalf of " + their_label + " !"
    else:
        response_message["status"] = 400
        response_message["error_response"] = response["messages"]
    
    return response_message


@app.get("/get-attributes/{h_type}")
async def get_attributes_by_type(h_type: str):
    
    schema_id = await get_schema_id(h_type)

    if schema_id != "":
        attributes = await get_schema_attributes(schema_id)

    return attributes


@app.get("/get-schema-id/{h_type}")
async def get_schema_id_by_type(h_type: str):
    
    schema_id = await get_schema_id(h_type)

    return schema_id


async def get_active_connection(their_label):

    async with aiohttp.ClientSession() as session:

        url = ISSUER_BASE_URL + "/connections"

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


async def declare_credential_info(holder_type, holder_attributes):

    schema_id = await get_schema_id(holder_type)
    cred_def_id = ""
    revocation = False

    if schema_id != "":
        cred_def_id = await get_credential_definition(schema_id)
        revocation = await support_revocation(cred_def_id)
        schema_is_valid = True
    else:
        schema_is_valid = False

    holder_attributes_set = set(holder_attributes)
    schema_attributes = await get_schema_attributes(schema_id)
    schema_attributes_set = set(schema_attributes)

    if holder_attributes_set == schema_attributes_set:
        attr_are_valid = True
        #Further check if attribute values are valid!
    else:
        attr_are_valid = False

    return schema_id, cred_def_id, revocation, schema_is_valid, attr_are_valid


async def accept_credential_proposal(h_type, their_label, attributes_values):

    attributes = []
    message = ""
    messages = []
    error_message = {}

    flag = False
    counter = len(attributes_values)
    connection_id = await get_active_connection(their_label)

    if counter > 0 and connection_id != "":
        for attribute in attributes_values:
            attributes.append(attribute["name"])
        schema_id, cred_def_id, revocation, schema_is_valid, attr_are_valid = await declare_credential_info(h_type, attributes)
        if schema_is_valid and attr_are_valid:
            flag = True
            credential = await create_credential(attributes_values, schema_id, cred_def_id, revocation, connection_id)
        else:
            message = "No registered schema found for the requested credential!"
            messages.append(message)
    elif counter <= 0:
        message = "The attributes for the credential were not set!"
        messages.append(message)
    elif connection_id == "":
        message = "Could not issue credential since no active connections were found!"
        messages.append(message)

    if flag == True:
        return flag, credential
    else:
        error_message["messages"] = messages
        return flag, error_message


if __name__ == '__main__':
    uvicorn.run("service:app", host="0.0.0.0", port=int(ISSUER_FastAPI_PORT))
