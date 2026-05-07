------------------Serverless CRUD Application Deployment on AWS--------------


A fully serverless CRUD application using:

AWS Lambda
API Gateway (REST API)
DynamoDB
Python 3.12

This project deploys:

A backend REST API for CRUD operations
A frontend HTML server using Lambda
DynamoDB for data storage


-------------------Architecture---------------------------------



User Browser
      │
      ▼
API Gateway (REST API)
      │
 ┌────┴────┐
 ▼         ▼
Frontend   Backend
Lambda     Lambda
                │
                ▼
           DynamoDB

----------------------------------------------------------------



Features :-
Fully serverless architecture
CRUD operations
REST API using API Gateway
DynamoDB integration
Frontend served directly from Lambda
CORS enabled
No EC2 servers required




---------------------------------------------------------------

Tech Stack   ::-


| Service     | Purpose                    |
| ----------- | -------------------------- |
| AWS Lambda  | Backend & Frontend compute |
| API Gateway | REST API                   |
| DynamoDB    | NoSQL database             |
| Python 3.12 | Runtime                    |
| IAM         | Permissions                |



--------------------------------------------------------------------
---------------------------------------------------------------------


STEP 1 — Create DynamoDB Table
Open AWS Console

Navigate to:
DynamoDB → Create Table
Configure:
Setting	Value
Table Name	UsersTable
Partition Key	id (String)

Click:
Create Table
Wait until status becomes:Active

---------------------------------------------------------------------
---------------------------------------------------------------------

STEP 2 — Create Backend Lambda (CRUD API)
Create Lambda Function
Navigate to:
AWS Lambda → Create Function

Configure:

Setting	Value
Function Name	UsersApiBackend
Runtime	Python 3.12
Upload Backend Code

Paste contents from:

backend/lambda_function.py
Update Configuration

At the top of the file:

REGION     = 'us-east-1'
TABLE_NAME = 'UsersTable'

Replace with your:

AWS Region
DynamoDB Table Name
Increase Timeout

Navigate:

Configuration → General Configuration

Set:

Timeout = 30 seconds
Add IAM Permissions

Navigate:

Configuration → Permissions
Click Lambda execution role
Add inline policy
Paste contents from:
iam_policy.json

This allows Lambda to access DynamoDB.


---------------------------------------------------------------------
---------------------------------------------------------------------

STEP 3 — Create Frontend Lambda (HTML Server)
Create Lambda

Navigate to:

Lambda → Create Function

Configure:

Setting	Value
Function Name	UsersApiFrontend
Runtime	Python 3.12
Upload Frontend Code

Paste contents from:

frontend/lambda_function.py
Configure Backend API URL

After API Gateway deployment (Step 4), update:

BACKEND_API_URL = 'https://YOUR_ID.execute-api.us-east-1.amazonaws.com/prod'

Example:

BACKEND_API_URL = 'https://1yyb2osu4l.execute-api.us-east-1.amazonaws.com/prod'
Deploy Lambda

Click:
Deploy

---------------------------------------------------------------------
---------------------------------------------------------------------

STEP 4 — Create API Gateway
4A. Create REST API

Navigate:

API Gateway → Create API → REST API → Build

Configure:

Setting	Value
API Name	UsersAPI
Endpoint Type	Regional
4B. Frontend Routes
Root Route /

The root resource already exists.

Create method:

Method	Integration
GET	Lambda Proxy → UsersApiFrontend

Enable:

Lambda Proxy Integration
Success Route /success

Create resource:

Setting	Value
Resource Name	success
Resource Path	success

Add method:

Method	Integration
GET	Lambda Proxy → UsersApiFrontend
4C. Backend Routes
Resource: /users

Create resource:

Setting	Value
Resource Name	users
Path	users

Enable:

Enable CORS
Methods for /users
Method	Lambda
GET	UsersApiBackend
POST	UsersApiBackend
OPTIONS	Auto-created

Enable:

Lambda Proxy Integration
Resource: /users/{id}

Create child resource under /users.

Setting	Value
Resource Name	{id}
Path	{id}

Enable:

Enable CORS
Methods for /users/{id}
Method	Lambda
GET	UsersApiBackend
PUT	UsersApiBackend
DELETE	UsersApiBackend
OPTIONS	Auto-created

Enable:

Lambda Proxy Integration
4D. Enable CORS
For /users

Enable:

Methods
GET, POST, OPTIONS
Headers
Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token
Gateway Responses
Default 4XX
Default 5XX
Origin
*
For /users/{id}

Enable:

Methods
GET, PUT, DELETE, OPTIONS
Headers
Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token
Gateway Responses
Default 4XX
Default 5XX
Origin
*
4E. Deploy API

Navigate:

API Actions → Deploy API

Create stage:

prod

Click:

Deploy
Copy Invoke URL

Example:

https://1yyb2osu4l.execute-api.us-east-1.amazonaws.com/prod
Final Application URL

Open in browser:

Live API URL

API Endpoints
Get All Users
GET /users
Get User By ID
GET /users/{id}
Create User
POST /users

Example Body:

{
  "id": "1",
  "name": "John",
  "email": "john@example.com"
}
Update User
PUT /users/{id}
Delete User
DELETE /users/{id}
Folder Structure
lambda-serverless-deploy/
│
├── backend/
│   └── lambda_function.py
│
├── frontend/
│   └── lambda_function.py
│
├── iam_policy.json
│
└── README.md
Security Notes
Frontend Lambda does NOT require DynamoDB access
Backend Lambda requires IAM permissions
Use least-privilege IAM policies in production
Restrict CORS origins in production environments
Troubleshooting
403 Forbidden

Check:

Lambda permissions
API Gateway deployment
Correct stage URL
CORS Errors

Verify:

OPTIONS methods exist
CORS enabled
Correct headers configured
DynamoDB Access Denied

Ensure IAM policy is attached to backend Lambda role.

Future Improvements
Authentication using Cognito/JWT
Terraform or AWS SAM deployment
CI/CD pipeline
CloudWatch logging
Custom domain
HTTPS certificate
Pagination & filtering

