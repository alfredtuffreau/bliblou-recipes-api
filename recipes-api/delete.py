import json
import os
import sys
sys.path.append("%s/recipes-api" % (os.getcwd()))
import response
import dynamodb 

# Env variables to configure dynamodb lib
tableRegion = os.environ["tableRegion"]
tableName = os.environ["tableName"]

def main(event, context):
  # prepare the key to delete in dynamodb recipe table
  key = { "recipeId": event["pathParameters"]["id"] }
  
  # Execute delete item in dynamodb
  try:
    dynamodb.call(tableRegion, tableName, "delete_item", Key=key)
  
  # Return 500 and status failed in case of error
  except:
    return response.failure(json.dumps({ "status": "false" }))
  
  # Return 200 in case of success
  else:
    return response.success(json.dumps({ "status": "true" }))