import os
import boto3
      
s3 = boto3.client("s3")

# Env variables to configure S3
bucket = os.environ["bucket"]

def main(event, context):
  # Handle every event records of deleted recipe pictures
  for record in event["Records"]:
    print("Handling event %s" % record)

    try:
      # List deleted file thumbnails
      deletedFile = record["s3"]["object"]["key"]
      file, ext = os.path.splitext(os.path.basename(deletedFile))
      response = s3.list_objects_v2(
        Bucket=bucket,
        Delimiter="/",
        Prefix="public/thumbnails/%s" % file
      )

      # Delete existing thumbnails
      if response.get("Contents"):
        for content in response["Contents"]:
          print("Deleting %s" % content["Key"])
          s3.delete_object(
            Bucket=bucket,
            Key=content["Key"]
          )
      
      # No thumbnails to delete
      else:
        print("No thumbnail found for %s" % deletedFile)
    # Log errors
    except Exception as e:
        print("An error occured: %s" % e)
    