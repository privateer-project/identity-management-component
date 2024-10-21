import asyncio
import json
import logging
import sys

from verifier import resolve_did, validate_did

logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)
#logging.basicConfig(filename='verifier.log', format='%(levelname)s - %(message)s', level=logging.INFO)

async def main():

    while True:
        print ("""
        1. Resolve DID.
        2. Exit/Quit
        """)

        try:
            option=input("What would you like to do? Enter the corresponding number: ")
        except KeyboardInterrupt:
            #print("\nExit...")
            logging.info(" Exit...")
            sys.exit() 
        
        if option=="1":
            # Resolve Issuer's DID.
            did = input("Enter a public DID to be resolved: ")
            did_is_valid, did = validate_did(did)
            if did_is_valid:
                did_document = await resolve_did(did)
                if did_document != {}:
                    print(json.dumps(did_document, indent=2))
                else:
                    #print('Could not resolve DID "did:sov:' + did + '".')
                    logging.info('Could not resolve DID "did:sov:' + did + '".')
            else:
                #print("Enter a valid DID.")
                logging.info("Enter a valid DID.")
        elif option=="2":
            #print("\nGoodbye")
            logging.info("Goodbye")
            break
        else:
            print("\nInvalid choice. Try again!")


asyncio.run(main())
