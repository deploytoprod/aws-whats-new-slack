import json
import feedparser
import boto3
import os
import botocore.exceptions
from datetime import datetime

# TODO: Implement Last-Modified given by feed response headers to save DDB WCU...

def dynamoTryInsert(i):
  try:
    now = datetime.now()
    ddbwrite = now.strftime("%m/%d/%Y, %H:%M:%S")
    dynamodb = boto3.client('dynamodb')
    print ("Inserting " + i.id)
    dynamodb.put_item(
      Item={
        'guid': {'S':i.id},
        'title': {'S': i.title},
        'link': {'S': i.link},
        'published': {'S': i.published},
        'ddbwrite': {'S': ddbwrite},
      },
        ConditionExpression='attribute_not_exists(guid)',
        TableName=os.environ['TABLE_NAME']
    )
  except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
      raise

def lambda_handler(event, context):
  feedUrl = 'https://aws.amazon.com/about-aws/whats-new/recent/feed/'
  d = feedparser.parse(feedUrl)

  for entry in d.entries:  # read one RSS entry at a time
    dynamoTryInsert(entry)


  return {
    'statusCode': 200,
    'body': json.dumps('Hello from Lambda!')
  }


