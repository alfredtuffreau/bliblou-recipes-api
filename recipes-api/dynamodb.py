import boto3

def call(action, tableName, item, region):
  dynamodb = boto3.resource("dynamodb", region_name=region)
  table = dynamodb.Table(tableName)
  
  getattr(table, action)(Item=item)