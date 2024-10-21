import aiohttp
import asyncio
import json
import logging
import subprocess
import sys

from issuer import get_issued_credentials, integer_within_range, revoke_credential, delete_credential

logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)
#logging.basicConfig(filename='issuer.log', format='%(levelname)s - %(message)s', level=logging.INFO)

async def main():

    while True:
        print ("""
        1. Revoke Credential
        2. Exit/Quit
        """)

        try:
            option=input("What would you like to do? Enter the corresponding number: ")
        except KeyboardInterrupt:
            #print("\nExit...")
            logging.info(" Exit...")
            sys.exit()

        if option=="1":
            cred_ids = await get_issued_credentials()
            if cred_ids != {}:
                print("Active credentials: ")
                print(json.dumps(cred_ids, indent=2))
                index = integer_within_range(cred_ids)
                rev_reg_id = cred_ids[index]["rev_reg_id"]
                cred_rev_id = cred_ids[index]["cred_rev_id"]
                connection_id = cred_ids[index]["connection_id"]           
                thread_id = cred_ids[index]["thread_id"]
                cred_ex_id = cred_ids[index]["cred_ex_id"]
                credential_revoked = await revoke_credential(rev_reg_id, cred_rev_id, connection_id, thread_id) # Revoke credential.
                #print(json.dumps(credential_revoked, indent=2))
                logging.info(credential_revoked["message"])
                credential_deleted = await delete_credential(cred_ex_id) # Delete revoked credential.
                #print(json.dumps(credential_deleted, indent=2))
                logging.info(credential_deleted["message"])
            else:
                #print("No credentials found!")
                logging.info("No credentials found!")
        elif option=="2":
            #print("\nGoodbye!")
            logging.info("Goodbye!")
            break
        else:
            print("\nInvalid choice. Try again!")


asyncio.run(main())