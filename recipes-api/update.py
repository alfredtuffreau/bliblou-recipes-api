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
  # Prepare item to update in db with event data
  data = json.loads(event["body"])
  
  if data.get("picture") is not None and data.get("content") is not None:
    updateExpression = "SET content = :content, picture = :picture, updatedAt = :updatedAt"
    expressionAttributeValues = { 
      ":picture": data["picture"], 
      ":content": data["content"], 
      ":updatedAt": str(datetime.datetime.now()),
    }
  
  elif data.get("content") is not None:
    updateExpression = "SET content = :content, updatedAt = :updatedAt"
    expressionAttributeValues = { ":content": data["content"], ":updatedAt": str(datetime.datetime.now()), }
  
  else:
    updateExpression = "SET picture = :picture"
    expressionAttributeValues = { ":picture": data["picture"] }
  
  # Execute update item in dynamodb
  try:
    dynamodb.call(tableRegion, tableName, "update_item", 
      Key={ "recipeId": event["pathParameters"]["id"] }, 
      UpdateExpression=updateExpression, 
      ExpressionAttributeValues=expressionAttributeValues, 
      ReturnValues="UPDATED_NEW"
    )
  
  # Return 500 and status failed in case of error
  except:
    return response.failure(json.dumps({ "status": "false" }))
  
  # Return 200 in case of success
  else:
    return response.success(json.dumps({ "status": "true" }))