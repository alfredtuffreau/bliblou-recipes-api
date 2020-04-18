def main(event):
  print(event)
  # for record in event["Records"]:
  #   filename = record["s3"]["object"]["key"]
  #   filesize = record["s3"]["object"]["size"]
  #   print('New object has been created: ', filename, ' (', filesize, ' bytes)')