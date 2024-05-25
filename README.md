# CDN-aaS

## Infrastructure:
### Main.py:

This acts as the gateway for the tenant to use our resources to create their own resources inside our cloud. It includes functionalities for tenant registration, login, and subsequent management of cloud resources. The script integrates email communications, database interactions for which we used sqlite, file management, and a command-line interface to facilitate these operations.

### Key Functionalities

Tenant Registration:
 
Users can register as tenants on our cloud platform by providing their name, email, and a password.
Upon registration, a unique tenant UUID (Universal Unique Identifier) is generated for each tenant and sent to their email for further usage.
The tenant's password is securely hashed using `bcrypt` before being stored in our database.
An email is sent to the tenant's email address with the UUID, using SMTP through Gmail’s email server.
The tenant’s details, including the hashed password and UUID, are stored in an SQLite database.

Tenant Login:

Tenants can log into our system by providing their registered email and password.
The system verifies the credentials against the stored values in the SQLite database.
Upon successful login, the tenant's UUID is written to a file for session management.

Email Communication:
 
The script has functionality to construct and send emails using `smtplib` and MIME standards. This is used during tenant registration to send a welcome email containing the tenant's UUID.

Session and File Management: 

Tenant UUIDs are managed through files; after login, a UUID is written to a file, which can be deleted upon logout to clean up the session.

Command-Line Interface:

The script provides a CLI for interacting with the system, with options to register, log in, and exit.

After login, tenants are provided with a menu to manage various cloud resources such as VPCs, Subnets, VMs, and Containers through associated scripts.

Database Management:

All tenant data is managed using SQLite. The script handles database connections, executes SQL queries to insert and fetch data, and commits changes to the database.


VPC (CRUD):

After the tenant logs in we provide them with the option of what they want to manage. For the tenants to manage the VPC we run a menu driven program that does the following:

Create_VPC.py 

This file acts as the northbound for taking in the user requirements such as VPC_name, Region and other requirements to run the backend create_vpc.yml. 


## SaaS:

### Upload:
Our first functionality will be upload which will be the place where the customers (content providers) provide their content (app) which needs to be distributed, subnet and the locations they want their app to be deployed in.

The input from the customer will be a JSON file that will have all the information mentioned above. This will be parsed in the upload script. The data (app) will then be stored in a storage and the mapping of stored app, subnet, and locations will be saved in a CSV file for future reference.

JSON input file example:
{
  "srcdata": "/home/vmadm/saas/app",
  "locations": ["loc1", "loc2"],
  "Subnet": "190.0.0.0/24"
}

We also generate a unique Customer ID for identification of each customer which will also be returned to the user.

### VM/Container Spin Up:
With the data and mapping we have all the necessary information to start a network and connect the VMs for a particular customer. Each customer will have his own subnet and network to provide isolation. Then we create the VMs in the customer network.

VM types = ['host', 'client', 'loc1', 'loc2', 'controller']

### Populate:
Once we have all the VMs up and running we need to populate them with customer data and functional code for our delivery to work. The app data (customer data to be distributed) will be populated in host and all the locations mentioned by the customer.
The functional code which is needed for the data to be delivered will be in the controller for it to do the delivery properly.
The controller will first get all the customer VMs in the network and their IPs stored. Then we will go ahead and start the apps in the edge servers i.e., host, loc1, loc2 after the apps are up and running we will have access to the content in those locations.

Fetch:
Now from the user perspective who is accessing the content of a particular customer. They will be providing three inputs: username, location, and which customer content they want to access (Customer ID). We will get the content from the backend in the controller.

