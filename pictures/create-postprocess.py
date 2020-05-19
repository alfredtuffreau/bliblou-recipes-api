import os
import sys
import datetime
import boto3
import tempfile
from PIL import Image, ImageEnhance
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
          while width < im.width and height < im.height:
            print("%s - create %d x %d thumbnail" % (eventId, width, height))
            thumbnail = file + "_%dx%d.jpeg" % (width, height)
            localPath = "/tmp/%s" % thumbnail
            resized_im = im.resize((width, height), Image.ANTIALIAS)

            contrast = 0.8
            while contrast <= 1.6:
              brightness = 0.8
              while brightness <= 1.6:

              # Enhance contrast after resize
              enhancer = ImageEnhance.Contrast(resized_im)
              contrasted_im = enhancer.enhance(contrast)

              # Enhance brightness after resize
              enhancer = ImageEnhance.Brightness(contrasted_im)
              final_im = enhancer.enhance(brightness)

              # Save image as tempfile
              localPath = "/tmp/%s" % thumbnail
              final_im.save(localPath, "JPEG", quality=100)

              # Upload resized image to S3 and record it as added thumbnail
              with open(localPath, "rb") as f:
                print("%s - uploading %s to thumbnails/ in %s" % (eventId, thumbnail, bucket))
                s3Path = "thumbnails/" + file + "_%dx%d_contrast%.1f_brightness%.1f.jpeg" % (width, height, contrast, brightness)
                s3.meta.client.upload_fileobj(f, bucket, "public/%s" % s3Path)
                addedThumbnails.append(s3Path)

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