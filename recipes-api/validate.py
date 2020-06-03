import json
import os
import sys
sys.path.append("%s/utils" % (os.getcwd()))
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
    recipe = dynamodb.call(tableRegion, tableName, "get_item", Key=key)
    
    # Return "item not found" and 500 with status failed when no item was found
    if recipe is None:
      return response.failure(json.dumps({ "status": "false", "error": "Item not found." }))
  
    print(recipe)

    # Updated the item with "validated" status and validatedAt date
    # updateExpression = "SET content = :content, validatedAt = :validatedAt"
    # expressionAttributeValues = { 
    #   ":content": data["content"], 
    #   ":validatedAt": str(datetime.datetime.now()),
    # }
    # updatedRecipe = dynamodb.call(tableRegion, tableName, "update_item", 
    #   Key={ "recipeId": event["pathParameters"]["id"] }, 
    #   UpdateExpression=updateExpression, 
    #   ExpressionAttributeValues=expressionAttributeValues, 
    #   ReturnValues="UPDATED_NEW"
    # )
    # return response.success(json.dumps(updatedRecipe, cls=DecimalEncoder))

  # Return 500 and status failed in case of error
  except:
    return response.failure(json.dumps({ "status": "false" }))