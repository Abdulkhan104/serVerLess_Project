import json
import boto3
import uuid
from datetime import datetime
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

# ═══════════════════════════════════════════════
#  CONFIGURATION  ← Edit these two lines
# ═══════════════════════════════════════════════
REGION     = 'us-east-1'       # ← Your AWS region
TABLE_NAME = 'UsersTable'      # ← Your DynamoDB table name

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table    = dynamodb.Table(TABLE_NAME)

CORS = {
    'Access-Control-Allow-Origin':  '*',
    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
}

# ───────────────────────────────────────────────
def resp(status, body):
    return {
        'statusCode': status,
        'headers': {**CORS, 'Content-Type': 'application/json'},
        'body': json.dumps(body, default=str)
    }

# ═══════════════════════════════════════════════
#  MAIN HANDLER
# ═══════════════════════════════════════════════
def lambda_handler(event, context):
    method  = event.get('httpMethod', '')
    params  = event.get('pathParameters') or {}
    user_id = params.get('id')

    try:
        body = json.loads(event.get('body') or '{}')
    except:
        return resp(400, {'error': 'Invalid JSON body'})

    try:
        if method == 'OPTIONS':                    return resp(200, {'ok': True})
        if method == 'GET'    and not user_id:     return get_all()
        if method == 'GET'    and user_id:         return get_one(user_id)
        if method == 'POST':                       return create(body)
        if method == 'PUT'    and user_id:         return update(user_id, body)
        if method == 'DELETE' and user_id:         return delete(user_id)
        return resp(405, {'error': f'Method {method} not allowed'})

    except ClientError as e:
        return resp(500, {'error': e.response['Error']['Message']})
    except Exception as e:
        return resp(500, {'error': str(e)})


# ═══════════════════════════════════════════════
#  CRUD FUNCTIONS
# ═══════════════════════════════════════════════

def get_all():
    """GET /users — returns all records (handles pagination)"""
    result = table.scan()
    items  = result.get('Items', [])
    while 'LastEvaluatedKey' in result:
        result = table.scan(ExclusiveStartKey=result['LastEvaluatedKey'])
        items.extend(result.get('Items', []))
    return resp(200, {'users': items, 'count': len(items)})


def get_one(user_id):
    """GET /users/{id} — returns single record"""
    result = table.get_item(Key={'id': user_id})
    item   = result.get('Item')
    if not item:
        return resp(404, {'error': f'User {user_id} not found'})
    return resp(200, {'user': item})


def create(body):
    """POST /users — creates new record with auto UUID"""
    for field in ['name', 'email']:
        if field not in body:
            return resp(400, {'error': f'Missing required field: {field}'})

    now  = datetime.utcnow().isoformat()
    item = {
        'id':         str(uuid.uuid4()),
        'name':       body['name'],
        'email':      body['email'],
        'phone':      body.get('phone', ''),
        'department': body.get('department', ''),
        'role':       body.get('role', 'user'),
        'status':     body.get('status', 'active'),
        'createdAt':  now,
        'updatedAt':  now,
    }
    table.put_item(Item=item)
    return resp(201, {'message': 'User created', 'user': item})


def update(user_id, body):
    """PUT /users/{id} — updates only the fields provided"""
    if not table.get_item(Key={'id': user_id}).get('Item'):
        return resp(404, {'error': f'User {user_id} not found'})

    fields = ['name', 'email', 'phone', 'department', 'role', 'status']
    exprs, vals, names = [], {}, {}

    for f in fields:
        if f in body:
            exprs.append(f'#_{f} = :_{f}')
            vals[f':_{f}']  = body[f]
            names[f'#_{f}'] = f

    if not exprs:
        return resp(400, {'error': 'No valid fields to update'})

    exprs.append('#_updatedAt = :_updatedAt')
    vals[':_updatedAt']  = datetime.utcnow().isoformat()
    names['#_updatedAt'] = 'updatedAt'

    result = table.update_item(
        Key={'id': user_id},
        UpdateExpression='SET ' + ', '.join(exprs),
        ExpressionAttributeValues=vals,
        ExpressionAttributeNames=names,
        ReturnValues='ALL_NEW'
    )
    return resp(200, {'message': 'User updated', 'user': result.get('Attributes', {})})


def delete(user_id):
    """DELETE /users/{id} — removes record"""
    if not table.get_item(Key={'id': user_id}).get('Item'):
        return resp(404, {'error': f'User {user_id} not found'})
    table.delete_item(Key={'id': user_id})
    return resp(200, {'message': 'User deleted', 'deletedId': user_id})
