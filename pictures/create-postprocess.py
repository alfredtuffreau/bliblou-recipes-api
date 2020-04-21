import os
import sys
import datetime
import boto3
import tempfile
from PIL import Image
sys.path.append("%s/utils" % (os.getcwd()))
import dynamodb
      
s3 = boto3.resource("s3")

bucket = os.environ["bucket"]
thumbnailWidth = int(os.environ["thumbnailWidth"])
thumbnailHeight = int(os.environ["thumbnailHeight"])
tableRegion = os.environ["tableRegion"]
tableName = os.environ["tableName"]

def main(event, context):
  for record in event["Records"]:
    eventId = record["eventID"]
    eventName = record["eventName"]
    recipeId = record["dynamodb"]["Keys"]["recipeId"]["S"]

    if eventName == "INSERT" and "NULL" not in record["dynamodb"]["NewImage"]["picture"]:
      picture = "public/%s" % record["dynamodb"]["NewImage"]["picture"]["S"]
      print("%s - %s: Creating thumbnails for recipe %s." % (eventId, eventName, recipeId))

      with tempfile.TemporaryFile() as f:
        print("Downloading %s from %s to tempfile..." % (picture, bucket))
        s3.meta.client.download_fileobj(bucket, picture, f)
        f.seek(0)
        
        file, ext = os.path.splitext(os.path.basename(picture))
        im = Image.open(f)
        if im.width / im.height >= thumbnailWidth / thumbnailHeight:
          width, height = int(im.width * thumbnailHeight / im.height), thumbnailHeight
        else:
          width, height = thumbnailWidth, int(im.height * thumbnailWidth / im.width)
        
        addedThumbnails = []
        while width < im.width and height < im.height:
          print("Create %d x %d thumbnail" % (width, height))
          thumbnail = file + "_%dx%d.jpeg" % (width, height)
          im.resize((width, height), Image.ANTIALIAS).save(thumbnail, "JPEG", quality=90)

          with open(thumbnail, "rb") as f:
            print("Uploading %s to thumbnails/ in %s" % (thumbnail, bucket))
            s3.meta.client.upload_fileobj(f, bucket, "public/thumbnails/%s" % thumbnail)
            addedThumbnails.append("thumbnails/%s" % thumbnail)

          width, height = width * 2, height * 2

    elif eventName == "MODIFY":
      print("Update existing")

    else:
      print("%s - %s: no action required." % (eventId, eventName))

    if addedThumbnails:
      print(addedThumbnails)
      dynamodb.call(tableRegion, tableName, "update_item", 
        Key={ "recipeId": recipeId }, 
        UpdateExpression="SET thumbnails = :thumbnails, updatedAt = :updatedAt", 
        ExpressionAttributeValues={ 
          ":thumbnails": addedThumbnails, 
          ":updatedAt": str(datetime.datetime.now()),
        }, 
        ReturnValues="UPDATED_NEW"
      )