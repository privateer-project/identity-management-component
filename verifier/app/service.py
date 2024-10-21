import aiohttp
import asyncio
import calendar
import datetime
import json
import re
import time
import uvicorn

from config import VERIFIER_BASE_URL, VERIFIER_FastAPI_PORT
from fastapi import FastAPI, Request
from verifier import get_active_connection, set_validity_period, get_schema_id_by_type, get_attributes_by_type, send_proof_request, verify_presentation

app = FastAPI()

@app.get("/request-invitation")
async def request_invitation():
    invitation: json = await create_oob_invitation()

    return invitation


async def create_oob_invitation():

    async with aiohttp.ClientSession() as session:

        url = VERIFIER_BASE_URL + "/out-of-band/create-invitation"

        data = {}
        data["use_public_did"] = False # True|False
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


@app.get("/request-verification")
async def request_verification(h_type: str, their_label: str):

    proof_received, response = await request_proof(h_type, their_label) # Presentation received.
    
    if proof_received == True:
        pres_ex_id = response
        time.sleep(2) # Otherwise, it does not display the correct state!
        state, verified = await verify_presentation(pres_ex_id)
    else:
        error_response = {}
        error_response["status"] = 400
        error_response["error_response"] = response["messages"]
        return error_response

    response = {}
    response["status"] = 200     
    if proof_received and state == "done" and verified != "":
        response["response"] = "Credential verified? " + verified + "!"
    else:
        response["response"] = "Could not verify holder " + their_label + ". State = " + state + "."
    return response


async def declare_schema_info(h_type):
    
    schema_id = await get_schema_id_by_type(h_type)

    attributes = await get_attributes_by_type(h_type)

    return schema_id, attributes


async def create_proof_request(schema_id, schema_attributes, epoch_datetime, connection_id, their_label, holder_type):
        
    requested_attributes = {}

    for attr in schema_attributes:
        attribute = {}
        restrictions = []
        restriction = {}
        attribute["name"] = attr
        restriction["schema_id"] = schema_id
        #restriction["attr::" + attr + "::value"] = "test_value" + attr[-1] # Add restriction about the credential value if needed. TODO Modify restriction (value)!
        restrictions.append(restriction)
        attribute["restrictions"] = restrictions
        requested_attributes["0_" + attr + "_uuid"] = attribute

    requested_predicates = {}
    presentation = {}
    presentation_request = {}
    indy = {}

    presentation["comment"] = "Verify entity " + their_label + "." # Optional
    presentation["connection_id"] = connection_id
    presentation["presentation_request"] = presentation_request

    presentation_request["indy"] = indy

    indy["name"] = "Proof for " + holder_type + " " + their_label + "."
    indy["version"] = "1.0"
    indy["requested_attributes"] = requested_attributes
    indy["requested_predicates"] = requested_predicates

    non_revoked = {}
    non_revoked["to"] = epoch_datetime
    indy["non_revoked"] = non_revoked #Optional

    #print(json.dumps(presentation, indent=2))
    return presentation


async def request_proof(h_type, their_label):

    epoch_datetime = set_validity_period()
    connection_id = await get_active_connection(their_label)
    schema_id, schema_attributes = await declare_schema_info(h_type)
    flag = False
    
    message = ""
    messages = []
    error_message = {}

    if connection_id != "":
        presentation = await create_proof_request(schema_id, schema_attributes, epoch_datetime, connection_id, their_label, h_type)
        if(isinstance(presentation, dict)):
            pres_ex_id = await send_proof_request(presentation)
            if pres_ex_id != "":
                flag = True
            else:
                message = "The presentation request was not successfully completed!"
                messages.append(message)
        else:
                message = "The presentation is not in proper format!"
                messages.append(message)
    else:
        message = "Could not create presentation since no active connections were found!"
        messages.append(message)

    if flag == True:
        return flag, pres_ex_id
    else:
        error_message["messages"] = messages
        return flag, error_message


if __name__ == '__main__':
    uvicorn.run("service:app", host="0.0.0.0", port=int(VERIFIER_FastAPI_PORT))
