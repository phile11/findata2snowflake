import json
import os
from datetime import UTC, datetime, timedelta

import boto3
import requests

s3 = boto3.client('s3')

def extract_eod_stockprices(api_url: str, timeout:tuple) -> list[dict]:
    """Extract new stock prices from the FMP api"""
    all_records = []
    apikey = os.environ['FMP_API_KEY']
    config_bucket = 'phile-findata1-configdata'
    key_file = 'dow30_test.json'
    yesterday = datetime.now(UTC) - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')

    #Loads config file from s3 which has the 87 free tier companies in it
    config_response = s3.get_object(Bucket=config_bucket, Key=key_file)
    config_content = config_response['Body'].read().decode('utf-8')
    json_config = json.loads(config_content)

    for ticker in json_config['dow30']:
        response = requests.get(
            api_url + ticker,
            params={'from': yesterday_str, 'to': yesterday_str, 'apikey': apikey},
            timeout=timeout
        )

        response.raise_for_status()
        data = response.json()
        all_records.extend(data)
       
    return all_records

def lambda_handler(event, context):
    api_url = 'https://financialmodelingprep.com/stable/historical-price-eod/full?symbol='
    timeout = (3.05, 30)
    filename = "stock_prices_raw_" + datetime.now(UTC).strftime("%Y%m%d_%H%M%S") + ".json"
    bucket = 'phile-findata1-raw-data'
    key_path = 'to_process/'

    stock_prices = extract_eod_stockprices(api_url, timeout)

    s3.put_object(
        Bucket=bucket,
        Key=key_path + filename,
        Body=json.dumps(stock_prices),
        ContentType='application/json'
    )
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


