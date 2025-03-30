# Installation Guide

The Self-Sovereign Identity (SSI) ecosystem consists of three key entities: the Holder, the Issuer, and the Verifier. Each of these entities is deployed as a separate Docker container. These containers can either run on the same Virtual Machine (VM) or on different VMs, depending on your setup.

In addition to the Holder, Issuer, and Verifier services, you will also need to install Hyperledger Indy for registering credential schemas and decentralized identifiers, as well as a Revocation Registry for enabling credential revocation. These components should be installed on the same VM.

## Installation of Indy Hyperledger and Revocation Registry

1. Ensure that Docker and Docker Compose are installed on your VM. If they are not installed, you can run the *prerequisites.sh* script provided in the repository to install these dependencies. Alternatively, you can install Docker and Docker Compose manually (recommended).
2. Move to your home directory and clone the source code of [Indy Hyperledger](https://github.com/bcgov/von-network) from the official GitHub repository.
   
   ```
   git clone https://github.com/bcgov/von-network.git
   ```
3. Navigate to the */von-network* directory and switch to a specific project version (v1.8.0). While the latest version may work, this implementation has been tested on this specific version.

   ```
   cd von-network
   git checkout tags/v1.8.0
   ```
4. Run the following command to build the Indy Hyperledger project:

   ```
   sudo ./manage build
   ```
5. Start the Indy Hyperledger container with the following command:
   
   ```
   sudo ./manage start
   ```
6. Return to your home directory and clone the source code of [Indy Tails Server](https://github.com/bcgov/indy-tails-server) from the official GitHub repository.
   
   ```
   git clone https://github.com/bcgov/indy-tails-server.git
   ```
7. Navigate to the */indy-tails-server* directory and switch to a specific project version (v1.1.0). While the latest version may work, this implementation has been tested on this specific version.

   ```
   cd indy-tails-server
   git checkout tags/v1.1.0
   ```
8. Build the Indy Tails Server by running:

   ```
   sudo ./docker/manage build
   ```
9. Start the Revocation Registry with the following command:
    
   ```
   sudo ./docker/manage start
   ```

## Installation and Setup for Holder, Issuer, and Verifier

1. Ensure that Docker and Docker Compose are installed on your VM. If they are not installed, you can run the *prerequisites.sh* script provided in the repository to install these dependencies.
2. Clone or download the source code of the service from the GitHub repository.
3. Navigate to the */identity-management-component/[entity]* directory. Replace *[entity]* with holder, issuer, or verifier, depending on the entity you wish to set up.
4. Edit the *.env* file, which contains all the required environment variables. This file allows you to configure the service, including IP addresses and other parameters. You can use a text editor to modify these variables as per your environment setup. It is mandatory to update the IP addresses; otherwise the service will not function. For the holder entity, you should also specify the desired architecture (either amd64 or arm64).
5. Start the holder, issuer, or verifier service, depending on the directory you are in.
6. Once the service is up and running, the respective entity will be initialized and ready for use. Run *main.py* script, which is responsible for establishing connections among other entities and performing operations related to Self-Sovereign Identity, such as credential issuance and verification.

### Issuer
```
git clone git@github.com:privateer-project/identity-management-component.git
cd identity-management-component
chmod +x ./prerequisites.sh
./prerequisites.sh
cd issuer
nano ./.env
sudo docker-compose up -d
sudo docker exec -it issuer bash -c "python app/main.py"
```

### Verifier
```
git clone git@github.com:privateer-project/identity-management-component.git
cd identity-management-component
chmod +x ./prerequisites.sh
./prerequisites.sh
cd verifier
nano ./.env
sudo docker-compose up -d
sudo docker exec -it verifier bash -c "python app/main.py"
```

### Holder
```
git clone git@github.com:privateer-project/identity-management-component.git
cd identity-management-component
chmod +x ./prerequisites.sh
./prerequisites.sh
cd holder
nano ./.env
sudo docker-compose up -d
sudo docker exec -it holder bash -c "python app/main.py"
```

**Note:** Before proceeding with the installation of the SSI entities, you must first set up the Indy Hyperledger and Indy Tails Server containers. Ensure both containers are up and running before moving forward. Additionally, the SSI entities must be deployed in the following sequence: i) issuer, ii) verifier and iii) holder. Failure to follow this order may cause communication errors between the entities. The Issuer must be deployed first and be ready to issue credentials, followed by the Verifier to verify those credentials, and finally the Holder, which will interact with both the Issuer and Verifier.

**Note:** The following table lists the four VMs currently running in the PRIVATEER Proxmox environment, along with their assigned IP addresses. Each VM is responsible for hosting a different component of the Self-Sovereign Identity ecosystem, including the Indy Hyperledger and Τails Server, as well as the Holder, Issuer, and Verifier agents.

| VM Name          | IP Address       |
| ---------------- | ---------------- |
| Indy Hyperledger | 10.160.3.38      |
| Issuer Agent     | 10.160.3.39      |
| Holder Agent     | 10.160.3.40      |
| Verifier Agent   | 10.160.3.41      |
