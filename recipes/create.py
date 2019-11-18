import os
import sys
sys.path.append("%s/recipes" % (os.getcwd()))

import uuid
import json
import datetime
import response
import dynamodb 
import boto3
rds = boto3.client('rds')

# Env variables to configure dynamodb lib
tableRegion = os.environ["tableRegion"]
tableName = os.environ["tableName"]

def main(event, context):
  try:
    dbs = rds.describe_db_instances()
    for db in dbs["DBInstances"]:
      print("{0}@{1}:{2} {3}".format(db["MasterUsername"], db["Endpoint"]["Address"], db["Endpoint"]["Port"], db["DBInstanceStatus"]))

  except Exception as e:
    print(e)

  # Prepare item to put in db with event data
  data = json.loads(event["body"])
  item = {
    "recipeId": str(uuid.uuid4()),
    "content": data["content"],
    "picture": data["picture"],
    "createdAt": str(datetime.datetime.now())
  }
  
  # Execute put item in dynamodb
  try:
    dynamodb.call("put_item", tableName, item, tableRegion)
  
  # Return 500 and status failed in case of error
  except Exception as e:
    print(str(e))
    return response.failure(json.dumps({ "status": "false" }))
  
  # Return 200 and added item in case of success
  else:
    return response.success(json.dumps(item))