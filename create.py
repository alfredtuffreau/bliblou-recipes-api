import uuid
import json
import os
import datetime
import sys
sys.path.append('./libs/')
import responseLib
import dynamodbLib

# Env variables to configure dynamodb lib
tableRegion = os.environ["tableRegion"]
tableName = os.environ["tableName"]

def main(event, context):
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
    dynamodbLib.call("put_item", tableName, item, tableRegion)
  
  # Return 500 and status failed in case of error
  except Exception as e:
    print(str(e))
    return responseLib.failure(json.dumps({ "status": "false" }))
  
  # Return 200 and added item in case of success
  else:
    return responseLib.success(json.dumps(item))