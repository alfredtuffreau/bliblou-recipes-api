import uuid
import json
import datetime
import os
import sys
sys.path.append("%s/recipes-api" % (os.getcwd()))
import response
import dynamodb 

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
    dynamodb.call(tableRegion, tableName, "put_item", Item=item)
  
  # Return 500 and status failed in case of error
  except:
    return response.failure(json.dumps({ "status": "false" }))
  
  # Return 200 and added item in case of success
  else:
    return response.success(json.dumps(item))