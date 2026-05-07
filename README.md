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

---------------------------------------------------------------











# 🚀 Two-Lambda Serverless Setup Guide
## Frontend Lambda + Backend Lambda + API Gateway + DynamoDB

---

## Architecture

```
Browser
  │
  ├── GET /          ──► Frontend Lambda  ──► returns index HTML
  ├── GET /success   ──► Frontend Lambda  ──► returns success HTML
  │
  └── /api/users     ──► Backend Lambda   ──► DynamoDB (CRUD)
       /api/users/{id}
```

---

## Project Files

```
project/
├── frontend/
│   └── lambda_function.py   ← Serves HTML pages (index + success)
├── backend/
│   └── lambda_function.py   ← REST API CRUD (GET/POST/PUT/DELETE)
└── SETUP_GUIDE.md
```

---

## STEP 1 — DynamoDB Table

1. AWS Console → **DynamoDB → Create Table**
2. Table name: `UsersTable`
3. Partition key: `id` (String)
4. Click **Create Table** → wait for status **Active**

---

## STEP 2 — Backend Lambda (CRUD API)

1. **Lambda → Create Function**
   - Name: `UsersApiBackend`
   - Runtime: Python 3.12
2. Paste contents of `backend/lambda_function.py`
3. Edit top of file:
   ```python
   REGION     = 'us-east-1'   # ← your region
   TABLE_NAME = 'UsersTable'  # ← your table name
   ```
4. **Configuration → General → Timeout**: 30 seconds
5. **Configuration → Permissions** → click the Role → Add inline policy from `iam_policy.json`

---

## STEP 3 — Frontend Lambda (HTML Server)

1. **Lambda → Create Function**
   - Name: `UsersApiFrontend`
   - Runtime: Python 3.12
2. Paste contents of `frontend/lambda_function.py`
3. **After deploying Backend API Gateway** (Step 4), come back and set:
   ```python
   BACKEND_API_URL = 'https://YOUR_ID.execute-api.us-east-1.amazonaws.com/prod'
   ```
4. Click **Deploy** in Lambda editor

> Frontend Lambda needs NO DynamoDB access — no extra IAM policy needed.

---

## STEP 4 — API Gateway (Single REST API for both Lambdas)

Create ONE API Gateway with two path groups:

### 4A. Create the API
- **API Gateway → Create API → REST API → Build**
- Name: `UsersAPI`
- Endpoint type: Regional

---

### 4B. Frontend Routes (serve HTML)

**Resource: /**
1. The root `/` already exists
2. Select `/` → Create Method → **GET**
   - Integration: Lambda Function
   - ✅ Lambda Proxy integration
   - Lambda: `UsersApiFrontend`

**Resource: /success**
1. Select `/` → Create Resource
   - Name: `success`, Path: `success`
2. Select `/success` → Create Method → **GET**
   - Integration: Lambda Proxy → `UsersApiFrontend`

---

### 4C. Backend Routes (REST API)

**Resource: /users**
1. Select `/` → Create Resource
   - Name: `users`, Path: `users`
   - ✅ Enable CORS
2. Add methods on `/users`:
   - **GET** → Lambda Proxy → `UsersApiBackend`
   - **POST** → Lambda Proxy → `UsersApiBackend`
   - **OPTIONS** → (auto-created by CORS)

**Resource: /users/{id}**
1. Select `/users` → Create Resource
   - Name: `{id}`, Path: `{id}`
   - ✅ Enable CORS
2. Add methods on `/users/{id}`:
   - **GET** → Lambda Proxy → `UsersApiBackend`
   - **PUT** → Lambda Proxy → `UsersApiBackend`
   - **DELETE** → Lambda Proxy → `UsersApiBackend`
   - **OPTIONS** → (auto-created by CORS)

---

### 4D. Enable CORS on both /users resources

For `/users`:
- ✅ Default 4XX, Default 5XX
- ✅ GET, POST, OPTIONS
- Headers: `Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token`
- Origin: `*`

For `/users/{id}`:
- ✅ Default 4XX, Default 5XX
- ✅ GET, PUT, DELETE, OPTIONS
- Headers: same as above
- Origin: `*`

---

### 4E. Deploy

1. **API actions → Deploy API**
2. Stage: `prod`
3. Click **Deploy**
4. **Copy the Invoke URL** → looks like:
   `https://abc123.execute-api.us-east-1.amazonaws.com/prod`

---

## STEP 5 — Connect Frontend Lambda to Backend

1. Open `frontend/lambda_function.py`
2. Set line 14:
   ```python
   BACKEND_API_URL = 'https://abc123.execute-api.us-east-1.amazonaws.com/prod'
   ```
3. Paste updated code into `UsersApiFrontend` Lambda
4. Click **Deploy**

---

## STEP 6 — Test Your App

Open in browser:
```
https://abc123.execute-api.us-east-1.amazonaws.com/prod/
```

That's it! No S3, no hosting — Lambda serves the HTML directly.

---

## API Endpoints Reference

| Method | Path            | Lambda  | Action        |
|--------|-----------------|---------|---------------|
| GET    | /               | Frontend| Dashboard     |
| GET    | /success        | Frontend| Success page  |
| GET    | /users          | Backend | Get all users |
| POST   | /users          | Backend | Create user   |
| GET    | /users/{id}     | Backend | Get one user  |
| PUT    | /users/{id}     | Backend | Update user   |
| DELETE | /users/{id}     | Backend | Delete user   |

---

## IAM Policy for Backend Lambda only

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem", "dynamodb:PutItem",
        "dynamodb:UpdateItem", "dynamodb:DeleteItem",
        "dynamodb:Scan", "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:615037471716:table/UsersTable"
    },
    {
      "Effect": "Allow",
      "Action": ["logs:CreateLogGroup","logs:CreateLogStream","logs:PutLogEvents"],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| White blank page | Check Frontend Lambda logs in CloudWatch |
| API calls fail | Verify `BACKEND_API_URL` has no trailing slash |
| CORS error | Redeploy API Gateway after enabling CORS |
| 502 on backend | Check Backend Lambda logs, verify TABLE_NAME |
| HTML shows raw text | Ensure `Content-Type: text/html` in Lambda response |
