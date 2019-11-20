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
  # Execute scan in dynamodb
  try:
    result = dynamodb.call(tableRegion, tableName, "scan")

  # Return 500 and status failed in case of error
  except:
    return response.failure(json.dumps({ "status": "false" }))

  # Return 200 and items in case of success
  else:
    return response.success(json.dumps(result["Items"], cls=DecimalEncoder))