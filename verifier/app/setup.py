import asyncio
import logging
import sys

from verifier import create_did, register_did, publish_did, get_public_did, get_private_did

logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)
#logging.basicConfig(filename='verifier.log', format='%(levelname)s - %(message)s', level=logging.INFO)

async def create_private_did():
    
    # Create a private DID.
    verifier_did = await get_private_did()
    if verifier_did == "":
        did, verkey = await create_did()
        verifier_did = did  
    #print('Verifier DID: ', verifier_did)
    logging.info('Verifier DID: %s', verifier_did)


async def create_public_did():
    
    # Create a public DID.
    verifier_did = await get_public_did()
    if verifier_did == "":
        did, verkey = await create_did()
        did = await register_did(did, verkey)
        did_published = await publish_did(did)
        verifier_did = did 
    #print('Verifier DID: ', verifier_did)
    logging.info('Verifier DID: %s', verifier_did)


# Create DID.
asyncio.run(create_private_did())
