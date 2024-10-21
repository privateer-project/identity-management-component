import asyncio
import logging

from issuer import create_did, register_did, publish_did, get_public_did, declare_schema_info, create_schema, get_schema_id, create_credential_definition, get_credential_definition

logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)
#logging.basicConfig(filename='issuer.log', format='%(levelname)s - %(message)s', level=logging.INFO)

async def create_did_and_schema():

    issuer_did = await get_public_did()
    if issuer_did == "":
        did, verkey = await create_did()
        did = await register_did(did, verkey)
        did_published = await publish_did(did)
        issuer_did = did
    #print('Issuer DID: ', issuer_did)
    logging.info('Issuer DID: %s', issuer_did)
    if issuer_did != "":
        schema = declare_schema_info()
        for schema_type, schema_info in schema.items():
            schema_id = await get_schema_id(schema_type)
            support_revocation = schema_info["support_revocation"]
            if schema_id != "":
                cred_def_id = await get_credential_definition(schema_id)
                if cred_def_id == "":
                    credential_definition_id = await create_credential_definition(schema_id, support_revocation)
            else:
                schema_name = schema_info["schema_name"]
                attributes = schema_info["attributes"]
                schema_id = await create_schema(schema_name, attributes)
                credential_definition_id = await create_credential_definition(schema_id, support_revocation)
    else:
        #print("Could not register the schema, since no DID was found for issuer " + ALIAS + ".")
        logging.info("Could not register the schema, since no DID was found for issuer " + ALIAS + ".")


# Create a public DID. Create and publish a Credential Schema on the Ledger.
asyncio.run(create_did_and_schema())