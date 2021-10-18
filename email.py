import requests
import json
import sys
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):

    # this code will catch the MODIFY event
    # The second part of the if statement ensure that handle_modify function runs only when the send key (minute 2)
    # got updated
    try:
        for record in event['Records']:
            if record['eventName'] == 'MODIFY' and record['dynamodb']['Keys']['id']['S'] == '2':
                handle_modify(record)
    except Exception as e:
        print(e)


def handle_modify(record):

    # this the auto email api, since we are not authorize to use SES
    url = "https://rapidprod-sendgrid-v1.p.rapidapi.com/mail/send"

    payload = "{\n  \"personalizations\": [\n    {\n      \"to\": [\n        {\n          \"email\": \"omar.shuaili@hotmail.com\"\n        }\n      ],\n      \"subject\": \"Hello, World!\"\n    }\n  ],\n  \"from\": {\n    \"email\": \"thetradingbot@tradingbot.com\"\n  },\n  \"content\": [\n    {\n      \"type\": \"text/plain\",\n      \"value\": \"Hi Omar Check out the price of APPLE stock\"\n    }\n  ]\n}"
    headers = {
        'content-type': "application/json",
        'x-rapidapi-key': "5d545caf53mshea139de8bfb6710p13cf8djsnc78d44f227e4",
        'x-rapidapi-host': "rapidprod-sendgrid-v1.p.rapidapi.com"
    }

    # A resource representing Amazon DynamoDB
    dynamodb = boto3.resource('dynamodb')

    # get the table name where prices stored.
    table = dynamodb.Table('PriceTBL')

    # this holds the new image (new price)
    newPrice = record['dynamodb']['NewImage']['price']['N']

    # this holds the old image (old price)
    oldPrice = record['dynamodb']['OldImage']['price']['N']

    # if statement to check if the second price modified
    if oldPrice != newPrice:

        # got the first price (minute 1 price ) and the second price (minute 2 price) from the table
        currentPrice = table.get_item(
            Key={
                'id': "2",
            }
        )
        previousPrice = table.get_item(
            Key={
                'id': "1",
            }
        )
        currentPrice = currentPrice['Item']['price']
        previousPrice = previousPrice['Item']['price']

        # here we have to check if both prices are holding real stock prices not just placeholders (-99)
        # we used -99 as placeholders to restart the filed in order to accept new real stock price
        if currentPrice != -99 and previousPrice != -99:

            # percentageChange variable calculate the percentage change between the previous minute price and the
            # current minute price
            percentageChange = ((currentPrice - previousPrice) / currentPrice) * 100

            # reset the prices to -99.
            table.update_item(
                Key={
                    'id': "1",
                },
                UpdateExpression="set price = :p",
                ExpressionAttributeValues={
                    ':p': -99
                })
            table.update_item(
                Key={
                    'id': "2",
                },
                UpdateExpression="set price = :p",
                ExpressionAttributeValues={
                    ':p': -99
                })
            table.update_item(
                Key={
                    'id': "3",
                },
                UpdateExpression="set price = :p",
                ExpressionAttributeValues={
                    ':p': percentageChange
                })

            # automatic email will be  sent if  percentageChange more than %0.5
            if percentageChange > 0.5:
                # automatic email request
                requests.request("POST", url, data=payload, headers=headers)
