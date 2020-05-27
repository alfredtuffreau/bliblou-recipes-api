import os
import sys
import datetime
import boto3
import tempfile
from PIL import Image
sys.path.append("%s/utils" % (os.getcwd()))
import dynamodb
      
s3 = boto3.resource("s3")

# Env variables to configure Pillow, dynamodb lib and S3
bucket = os.environ["bucket"]
thumbnailWidth = int(os.environ["thumbnailWidth"])
thumbnailHeight = int(os.environ["thumbnailHeight"])
tableRegion = os.environ["tableRegion"]
tableName = os.environ["tableName"]

def shouldCreateThumbnail(eventName, dynamodbEvent):
  if eventName == "INSERT" and "NULL" not in dynamodbEvent["NewImage"]["picture"]:
    return True
  
  if eventName == "MODIFY" and "NULL" not in dynamodbEvent["NewImage"]["picture"]:
    oldImage = dynamodbEvent["OldImage"]
    newImage = dynamodbEvent["NewImage"]
    
    if "NULL" in oldImage["picture"] or oldImage["picture"]["S"] != newImage["picture"]["S"]:
      return True
  
  return False

def main(event, context):
  # Handle every event records on dynamodb table
  for record in event["Records"]:
    eventId = record["eventID"]
    print("Handling event %s - %s" % (eventId, record))

    try:
      # No thumbnail creation needed
      if not shouldCreateThumbnail(record["eventName"], record["dynamodb"]):
        print("%s - no action required." % eventId)
      
      # Thumbnails creation needed
      else:
        recipeId = record["dynamodb"]["Keys"]["recipeId"]["S"]
        print("%s - creating thumbnails for recipe %s." % (eventId, recipeId))
        addedThumbnails = []

        # Create and upload thumbnails
        with tempfile.TemporaryFile() as f:
          picture = "public/%s" % record["dynamodb"]["NewImage"]["picture"]["S"]
          print("%s - downloading %s from %s to tempfile..." % (eventId, picture, bucket))
          print(s3.meta.client.head_object(Bucket=bucket, Key=picture)["ResponseMetadata"]["HTTPHeaders"]["content-length"])
          original_size = s3.meta.client.head_object(Bucket=bucket, Key=picture)["ResponseMetadata"]["HTTPHeaders"]["content-length"]
          s3.meta.client.download_fileobj(bucket, picture, f)
          f.seek(0)
          file, ext = os.path.splitext(os.path.basename(picture))
          im = Image.open(f)
          
          # Compute the min thumbnail size
          if im.width / im.height >= thumbnailWidth / thumbnailHeight:
            width, height = int(im.width * thumbnailHeight / im.height), thumbnailHeight
          else:
            width, height = thumbnailWidth, int(im.height * thumbnailWidth / im.width)
            
          # Resize image with size < original size
          thumbnailIsBigger = False
          while width < im.width and height < im.height and not thumbnailIsBigger:
            print("%s - create %s%s %d x %d thumbnail" % (eventId, file, ext, width, height))
            thumbnail = file + "_%dx%d.png" % (width, height)
            localPath = "/tmp/%s" % thumbnail
            im.resize((width, height), Image.ANTIALIAS).save(localPath, "PNG", optimize=True, quality=75)

            # Upload resized image to S3 and record it as added thumbnail if size < original size
            if int(original_size) > int(os.stat(localPath).st_size)
              with open(localPath, "rb") as f:
                print("%s - uploading %s to thumbnails/ in %s" % (eventId, thumbnail, bucket))
                s3Path = "thumbnails/%s" % thumbnail
                s3.meta.client.upload_fileobj(f, bucket, "public/%s" % s3Path)
                addedThumbnails.append(s3Path)
            else: 
              thumbnailIsBigger = True

            # Update while conditions
            width, height = width * 2, height * 2

        # Update recipe with added thumbnails
        if addedThumbnails:
          print("%s - updating recipe %s with added thumbnails %s" % (eventId, recipeId, ", ".join(addedThumbnails)))
          dynamodb.call(tableRegion, tableName, "update_item", 
            Key={ "recipeId": recipeId }, 
            UpdateExpression="SET thumbnails = :thumbnails, updatedAt = :updatedAt", 
            ExpressionAttributeValues={ ":thumbnails": addedThumbnails, ":updatedAt": str(datetime.datetime.now()) }, 
            ReturnValues="UPDATED_NEW"
          )
    
    # Log errors
    except Exception as e:
        print("%s - an error occured: %s" % (eventId, e))