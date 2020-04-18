def main(event, context):
  for record in event["Records"]:
    filename = record["s3"]["object"]["key"]
    filesize = record["s3"]["object"]["size"]
    print('An object has been deleted: ', filename, ' (', filesize, ' bytes)')