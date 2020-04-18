def main(event, context):
  for record in event["Records"]:
    filename = record["s3"]["object"]["key"]
    filesize = record["s3"]["object"]["size"]
    print('New object has been created: %(filename)s (%(filesize)d bytes)' %
          { "filename": filename, "filesize": filesize})