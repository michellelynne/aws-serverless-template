import boto3
import json
import logging
import os

from base64 import b64decode, b64encode
from botocore.exceptions import ProfileNotFound
from copy import deepcopy

AWS_REGION = os.environ.get('AWS_REGION')
TABLE_NAME = os.environ.get('TABLE_NAME')
SECRET_NAME = os.environ.get('SECRET_NAME')

try:
    boto3.setup_default_session(profile_name='personal')
except ProfileNotFound:
    pass

if AWS_REGION:
    dynamodb_client = boto3.resource('dynamodb', region_name=AWS_REGION)
    kms_client = boto3.client('kms', region_name=AWS_REGION)
if TABLE_NAME:
    table = dynamodb_client.Table(TABLE_NAME)

# TODO: Needs work.
# import sentry_sdk
# from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
# sentry_sdk.init(
#     SENTRY_DSN,
#     integrations=[AwsLambdaIntegration()]
# )

logger = logging.getLogger()
logHandler = logging.StreamHandler()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """Item Lambda function

    This lambda is invoked by GET or POST API request,
    it adds/reads info into DynamoDB table.

    Arguments:
        event LambdaEvent -- Lambda Event received from Invoke API.
        context LambdaContext -- Lambda Context runtime methods and attributes.

    Returns:
        dict -- {'statusCode': int, 'body': dict}
    """
    if event['httpMethod'] == 'GET':
        return get_handler(event, context)
    elif event['httpMethod'] == 'POST':
        return post_handler(event, context)
    elif event['httpMethod'] == 'PUT':
        return put_handler(event, context)
    elif event['httpMethod'] == 'DELETE':
        return delete_handler(event, context)
    else:
        raise NotImplementedError()


def get_handler(event, context):
    logger.info('Starting lambda handler for GET request.')
    path_parameters = event.get('pathParameters')
    path_id = None
    if path_parameters:
        path_id = path_parameters.get('ID')
    if path_id:
        path_id = int(path_id)
        db_response = table.get_item(Key={'id': path_id})
        item = db_response['Item']
        response = {
            'statusCode': db_response['ResponseMetadata']['HTTPStatusCode'],
            'body': json.dumps(item),
            'isBase64Encoded': False
        }
    else:
        db_response = table.scan()
        items = db_response['Items']
        response = {
            'statusCode': db_response['ResponseMetadata']['HTTPStatusCode'],
            'body': json.dumps(items),
            'isBase64Encoded': False
        }
    logger.info('DynamoDB response:{}'.format(db_response['ResponseMetadata']))
    return response


def post_handler(event, context):
    logger.info('Item POST request.')
    new_item = deepcopy(json.loads(event['body']))
    response = table.put_item(Item=new_item)
    logger.info('Item {} added to table.'.format(new_item['id']))
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }


def put_handler(event, context):
    logger.info('Item PUT request.')
    modified_item = deepcopy(json.loads(event['body']))
    path_id = event['pathParameters'].get('ID')
    if not modified_item.get('id'):
        modified_item['id'] = path_id
    response = table.put_item(Item=modified_item)
    logger.info('Item {} modified.'.format(modified_item['id']))
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }


def delete_handler(event, context):
    logger.info('Item DELETE request.')
    path_id = event['pathParameters'].get('ID')
    path_id = int(path_id)
    db_response = table.delete_item(Key={'id': path_id})
    response = {
        'statusCode': db_response['ResponseMetadata']['HTTPStatusCode'],
        'body': '',
        'isBase64Encoded': False
    }
    logger.info('Item {id} deleted.'.format(id=path_id))
    return response


def encrypt_string(source_plaintext):
    """Encrypts a string using a KMS alias.

    Args:
        source_plaintext(str): String to encrypt.

    Returns:
        str: Encrypted data.

    """
    encrypted_response = kms_client.encrypt(Plaintext=source_plaintext, KeyId=KMS_ALIAS)
    return b64encode(encrypted_response['CiphertextBlob']).decode('utf-8')


def decrypt_string(encrypted_string):

    """Decrypts a string using a KMS

    Args:
        encrypted_string(str): Encrypted string.

    Returns:
        str: Plaintext string.

    """
    decrypted_response = kms_client.decrypt(CiphertextBlob=b64decode(encrypted_string))
    return decrypted_response['Plaintext'].decode('utf-8')


def get_secret():
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=AWS_REGION
    )
    get_secret_value_response = client.get_secret_value(
        SecretId=SECRET_NAME
    )
    return json.loads(get_secret_value_response['SecretString'])

