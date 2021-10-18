import pandas as pd
import boto3

from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    string = "dfghj"
    encoded_string = string.encode("utf-8")
    s3 = boto3.client('s3')
    bucket = 'excelzainab'
    key = 'excel'

    excelFile = s3.get_object(Bucket=bucket, Key=key)

    # Read and store content
    # of an excel file
    read_file = pd.read_excel(excelFile)

    # Write the dataframe object
    # into csv file
    read_file.to_csv("convertedExcel.csv",
                     index=None,
                     header=True)

    # read csv file and convert
    # into a dataframe object
    df = pd.DataFrame(pd.read_csv("convertedExcel.csv"))

    s3_path = "excel.xlsx"

    s3 = boto3.resource("s3")
    s3.Bucket(bucket).put_object(Key=s3_path, Body=encoded_string)


