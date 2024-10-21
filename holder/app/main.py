import asyncio
import json
import logging
import sys
import time

from config import ISSUER_FastAPI_BASE_URL, VERIFIER_FastAPI_BASE_URL
from holder import request_invitation, receive_oob_invitation, create_credential_proposal, get_credential_proposal_info, get_credentials, credential_already_exists, get_credential_state_by_id, delete_revoked_credential, request_credential, request_verification, delete_active_connection

logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)
#logging.basicConfig(filename='holder.log', format='%(levelname)s - %(message)s', level=logging.INFO)

async def main():

    while True:
        print ("""
        1. Request and Receive Credential.
        2. Request to be verified.
        3. Exit/Quit
        """)

        try:
            option=input("What would you like to do? Enter the corresponding number: ")
        except KeyboardInterrupt:
            #print("\nExit...")
            logging.info(" Exit...")
            sys.exit()

        if option=="1":
            #print("\nRequest and Receive Connection Invitation. Request and Receive Credential.")
            BASE_URL = ISSUER_FastAPI_BASE_URL
            invitation = await request_invitation(BASE_URL)
            if invitation != {}:
                sender = invitation["label"]
                connection_id = await receive_oob_invitation(invitation, sender)
                time.sleep(2) # Otherwise, it does not display the correct state!
                if connection_id != "":
                    #print("Connection Holder-Issuer established. Connection ID: ", connection_id)
                    logging.info("Connection Holder-Issuer established. Connection ID: %s", connection_id)
                    credential_proposal = await create_credential_proposal(connection_id)
                    attributes_values = credential_proposal["credential_preview"]["attributes"]
                    credential_attributes, credential_attributes_values = get_credential_proposal_info(attributes_values)
                    credentials = await get_credentials()
                    credential_exists, credential_id = credential_already_exists(credentials, credential_attributes, credential_attributes_values)
                    if credential_exists:
                        credential_revoked = await get_credential_state_by_id(credential_id)
                        if credential_revoked:
                            revoked_credential_deleted = await delete_revoked_credential(credential_id)
                            #print(json.dumps(revoked_credential_deleted, indent=2))
                            credential_received = await request_credential(credential_proposal)
                        else:
                            credential_received = {}
                            credential_received["response"] = "A valid credential already exists!"
                    else:
                        credential_received = await request_credential(credential_proposal)
                    
                    if credential_received != {}:
                        #print(json.dumps(credential_received, indent=2)) # Uncomment this.
                        message = ""
                        if "response" in credential_received:
                            message = credential_received["response"]
                            stored_credentials = await get_credentials()
                            #print(json.dumps(stored_credentials, indent=2)) # Uncomment this.
                        elif "error_response" in credential_received:
                            error_response = ' '.join(credential_received["error_response"])
                            message = "Error response: " + error_response
                        logging.info('%s', message)
                else:
                    #print("Could not request credential since no active connections were found!")
                    logging.info("Could not request credential since no active connections were found!")
            else:
                #print("Could not establish connection between Holder and Issuer!")
                logging.info("Could not establish connection between Holder and Issuer!")
        elif option=="2":
            #print("\nRequest and Receive Connection Invitation. Request Verification.")
            BASE_URL = VERIFIER_FastAPI_BASE_URL
            invitation = await request_invitation(BASE_URL)
            if invitation != {}:
                sender = invitation["label"]
                connection_id = await receive_oob_invitation(invitation, sender)
                time.sleep(2) # Otherwise, it does not display the correct state!
                if connection_id != "":
                    #print("Connection Holder-Verifier established. Connection ID: ", connection_id)
                    logging.info("Connection Holder-Verifier established. Connection ID: %s", connection_id)
                    presentation_verified = await request_verification()
                    if presentation_verified != {}:
                        #print(json.dumps(presentation_verified, indent=2))
                        message = ""
                        if "response" in presentation_verified:
                            message = presentation_verified["response"]
                        elif "error_response" in presentation_verified:
                            error_response = ' '.join(presentation_verified["messages"])
                            message = "Error response: " + error_response
                        logging.info('%s', message)
                        connection_deleted = await delete_active_connection(connection_id)
                        #print(json.dumps(connection_deleted, indent=2))
                else:
                    #print("Could not be verified since no active connections were found!")
                    logging.info("Could not be verified since no active connections were found!")
            else:
                #print("Could not establish connection between Holder and Verifier!")
                logging.info("Could not establish connection between Holder and Verifier!")
        elif option=="3":
            #print("\nGoodbye")
            logging.info("Goodbye")
            break
        else:
            print("\nInvalid choice. Try again!")


#asyncio.run(main())
if __name__ == "__main__":
    asyncio.run(main())
