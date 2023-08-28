import json
import boto3
import requests
from boto3.dynamodb.types import TypeDeserializer
import decimal
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import botocore.exceptions
import os
from time import sleep
import base64
import hmac
import hashlib
import re


def postToSlack(msg):

  headers = {
      'Content-Type': 'application/json',
  }

  data = "{\"Content\":\""+msg+"\"}"
  try:
    ssm = boto3.client('ssm')
    ssmparam = ssm.get_parameters(
        Names=[os.environ['PARAMETER_NAME']],
        WithDecryption=True
    )
  except ClientError as error:
    print('Problem getting keys from SSM: {}'.format(error))
    return {
        'statusCode': 501,
        'body': 'Problem getting parameter'
    }
  paramvalue = ssmparam['Parameters'][0]['Value']
  print ("Data sent to webhook:" + data)
  response = requests.post(paramvalue, headers=headers, data=data)


def lambda_handler(event, context):

  for record in event['Records']:
    try:
      link = record['dynamodb']['NewImage']['link']['S']
      title = record['dynamodb']['NewImage']['title']['S']
      published = record['dynamodb']['NewImage']['published']['S']
      msg = title + " [" + link + "]: published at " + published
      txt = re.sub(u'\u2014', '--', msg)  # Replacing em dash
      txt = re.sub(u'\u2019', '\'', txt)  # Replacing incorrect apostrophe
      txt = re.sub('\+0000', 'GMT', txt)  # Replacing timezone for GMT
      print("Msg (without modifications): " + msg)
      print("Txt (with fixes): " + txt)
      postToSlack(txt)
      sleep(1)
    except:
      pass

  return {
      'statusCode': 200,
      'body': json.dumps('Hello from Lambda!')
  }
