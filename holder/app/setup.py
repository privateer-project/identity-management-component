import asyncio
import logging

from holder import create_did, register_did, publish_did, get_public_did, get_private_did

logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)
#logging.basicConfig(filename='holder.log', format='%(levelname)s - %(message)s', level=logging.INFO)

async def create_private_did():
    
    # Create a private DID.
    holder_did = await get_private_did()
    if holder_did == "":
        did, verkey = await create_did()
        holder_did = did
    #print('Holder DID: ', holder_did)
    logging.info('Holder DID: %s', holder_did)


async def create_public_did():
    
    # Create a public DID.
    holder_did = await get_public_did()
    if holder_did == "":
        did, verkey = await create_did()
        did = await register_did(did, verkey)
        did_published = await publish_did(did)
        holder_did = did
    #print('Holder DID: ', holder_did)
    logging.info('Holder DID: %s', holder_did)


# Create DID.
asyncio.run(create_private_did())

