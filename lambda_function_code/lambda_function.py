import json
import boto3
import uuid
import logging
from boto3.dynamodb.conditions import Key, Attr, And
import functools

ec2= boto3.client('ec2', region_name = 'us-east-1' )
dynamodb = boto3.resource('dynamodb', region_name = 'us-east-1')
db_table = "my-dynamodb-demo"
table = dynamodb.Table(db_table)

logger = logging.getLogger()
logger.setLevel("INFO")

def logint(func):
    def inner(event, context):
        try:
            logger.info(f'Request Received: {json.dumps(event)}')
            status_code, response = func(event, context)
            response = {
                'statusCode': status_code,
                'body': json.dumps(response)
            }
            logger.info(f'Response Sent: {response}')
            return response
        except Exception as e:
            logger.error(e)
            return {
                'statusCode': 500,
                'body': json.dumps('Internal Server Error')
            }
    return inner

@logint
def lambda_handler(event, context):
    try:
        path = event['path']
        http_method = event['httpMethod']
        if http_method == "GET":
            status_code, response = get_ops(event)
            return status_code, response
        elif http_method == "POST":
            status_code, response = create_resources(event)
            return status_code, response
    except Exception as e:
        logger.error(f'Exception occured: {e}')
        return 500, 'Internal Server Error'


def get_ops(event):
    """Get DynamoDB operations"""
    logger.info('In Get operations')
    if event.get('queryStringParameters'):
        queryStringParameters = event['queryStringParameters']
        vpc_name = queryStringParameters.get('vpc_name')
        response = table.query(
            KeyConditionExpression=(Key('vpc-name').eq(vpc_name))
            # FilterExpression=functools.reduce(And, ([Key(k).eq(v) for k, v in queryStringParameters.items()]))
        )
        logger.info(response)
    else:
        response = table.scan()

    if response.get('Items'):
        return 200, response['Items']
    else:
        return 200, 'No items found'

def create_resources(event):
    """Create VPC and subnets"""
    logger.info('In Create operations')
    body = json.loads(event['body'])
    vpc_name = body.get('vpc_name')
    cidr_block = body.get('cidr_block')
    region = body.get('region')
    subnet_to_be_created = body.get('subnet_to_be_created')
    if not vpc_name or not cidr_block or not region or not subnet_to_be_created:
        return 400, 'Missing required parameters'

    response = table.get_item(Key={'vpc-name': vpc_name})
    if response.get('Item'):
        Item = response.get('Item')
        if Item.get('vpc-name') == vpc_name:
            return 200, 'VPC already exists'
        
    vpc_response = ec2.create_vpc(CidrBlock=cidr_block)
    logger.info(f'VPC created: {vpc_response}')

    vpc_id = vpc_response['Vpc']['VpcId']
    vpc_tags = ec2.create_tags(Resources=[vpc_id], Tags=[{'Key': 'Name', 'Value': vpc_name}])
    logger.info(f'VPC name tagged: {vpc_tags}')

    subnets = []
    for i in range(subnet_to_be_created):
        subnet_response = ec2.create_subnet(CidrBlock=f'10.20.{i}.0/24', VpcId=vpc_id)
        subnet_id = subnet_response['Subnet']['SubnetId']
        subnet_name = body.get(f'subnet_name_{i+1}')
        ec2.create_tags(Resources=[subnet_id], Tags=[{'Key': 'Name', 'Value': subnet_name}])
        subnets.append(subnet_id)

    logger.info(f'Subnets created: {subnets}')

    response = table.put_item(Item={'vpc-name':vpc_name, 'vpc_id': vpc_id, 'cidr_block':cidr_block, 'region':region, 'subnets': subnets})
    logger.info('Data successfully inserted to DB')

    return 200, 'Resources created successfully'
