import boto3
from boto3.dynamodb.conditions import Key

def call(region, tableName, action, **kwargs):
  dynamodb = boto3.resource("dynamodb", region_name=region)
  table = dynamodb.Table(tableName)

  return getattr(table, action)(**kwargs)