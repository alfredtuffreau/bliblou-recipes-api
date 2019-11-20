import json
import os
import sys
sys.path.append("%s/recipes-api" % (os.getcwd()))
import response
import dynamodb 
from decimalEncoder import DecimalEncoder

# Env variables to configure dynamodb lib
tableRegion = os.environ["tableRegion"]
tableName = os.environ["tableName"]

def main(event, context):
  # prepare the key to search in dynamodb recipe table
  key = { "recipeId": event["pathParameters"]["id"] }
  
  # Execute get item in dynamodb
  try:
    result = dynamodb.call(tableRegion, tableName, "get_item", Key=key)

  # Return 500 and status failed in case of error
  except:
    return response.failure(json.dumps({ "status": "false" }))

  else:
    # Return 200 and the retrieved item
    if result is not None:
      return response.success(json.dumps(result["Item"], cls=DecimalEncoder))
    
    # Return "item not found" and 500 with status failed when no item was found
    else:
      return response.failure(json.dumps({ "status": "false", "error": "Item not found." }))