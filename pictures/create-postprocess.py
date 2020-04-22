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
    print("Handling event %s - %s" % (eventId, record))

    try:
      eventName = record["eventName"]
      if eventName == "INSERT" and "NULL" not in record["dynamodb"]["NewImage"]["picture"]:
        recipeId = record["dynamodb"]["Keys"]["recipeId"]["S"]
        print("%s - creating thumbnails for recipe %s." % (eventId, recipeId))

        with tempfile.TemporaryFile() as f:
          picture = "public/%s" % record["dynamodb"]["NewImage"]["picture"]["S"]
          print("%s - downloading %s from %s to tempfile..." % (eventId, picture, bucket))
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
          print("%s - create %d x %d thumbnail" % (eventId, width, height))
          thumbnail = file + "_%dx%d.jpeg" % (width, height)
          localPath = "/tmp/%s" % thumbnail
          im.resize((width, height), Image.ANTIALIAS).save(localPath, "JPEG", quality=90)

          with open(localPath, "rb") as f:
            print("%s - uploading %s to thumbnails/ in %s" % (eventId, thumbnail, bucket))
            s3Path = "thumbnails/%s" % thumbnail
            s3.meta.client.upload_fileobj(f, bucket, "public/%s" % s3Path)
            addedThumbnails.append(s3Path)

          width, height = width * 2, height * 2

        if addedThumbnails:
          print("%s - updating recipe %s with added thumbnails %s" % (eventId, recipeId, ", ".join(addedThumbnails)))
          dynamodb.call(tableRegion, tableName, "update_item", 
            Key={ "recipeId": recipeId }, 
            UpdateExpression="SET thumbnails = :thumbnails, updatedAt = :updatedAt", 
            ExpressionAttributeValues={ 
              ":thumbnails": addedThumbnails, 
              ":updatedAt": str(datetime.datetime.now()),
            }, 
            ReturnValues="UPDATED_NEW"
          )

      else:
        print("%s - no action required." % eventId)
    
    except Exception as e:
        print("%s - an error occured: %s" % (eventId, e))