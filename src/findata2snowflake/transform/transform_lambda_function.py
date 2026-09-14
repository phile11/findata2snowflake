"""This code is for running as an AWS Lambda function"""
import json
from datetime import UTC, datetime
from io import StringIO

import boto3
import pandas as pd

s3 = boto3.client("s3")

def daily_stock_price(data):
    stockprice_list = []
    for row in data:
        date = row['date']
        symbol = row['symbol']
        open_price = row['open']
        high_price = row['high']
        low_price = row['low']
        close_price = row['close']
        vwap = row['vwap']
        volume = row['volume']
        price_change = row['change']
        price_change_percent = row['changePercent']
        stockprice_list.append({
            'date': date,
            'symbol': symbol,
            'open_price': open_price,
            'high_price': high_price,
            'low_price': low_price,
            'close_price': close_price,
            'vwap': vwap,
            'volume': volume,
            'price_change': price_change,
            'price_change_percent': price_change_percent
        })
    return stockprice_list

def lambda_handler(event, context):
    Bucket = "phile-findata1-raw-data"
    Key = "to_process/"
    all_stock_data = []

    # List all files waiting to be processed
    response = s3.list_objects(Bucket=Bucket, Prefix=Key)
    stockprice_files = [file['Key'] for file in response['Contents'] if 'stock_prices' in file['Key']]

    for file_key in stockprice_files:
    # Read raw JSON from S3
        response = s3.get_object(Bucket=Bucket, Key=file_key)
        content = response['Body'].read().decode('utf-8')
        data = json.loads(content)
        all_stock_data.extend(data)

    # Use Transform function
    stockprice_list = daily_stock_price(all_stock_data)

    # Create DataFrames & dedup
    stockprice_df = pd.DataFrame(stockprice_list).drop_duplicates(subset=['date', 'symbol'])

    # Convert dates
    stockprice_df['date'] = pd.to_datetime(stockprice_df['date'], format='%Y-%m-%d')

    # Write transformed data to S3 as CSV
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    for df, name in [(stockprice_df, "daily_stock_prices")]:
        buffer = StringIO()
        df.to_csv(buffer, index=False)
        s3.put_object(
            Bucket="phile-findata1-transformed-data",
            Key=f"{name}/{name}_transformed_{timestamp}.csv",
            Body=buffer.getvalue()
        )
    for file_key in stockprice_files:
        # Move processed file to 'processed' folder
        copy_source = {'Bucket': Bucket, 'Key': file_key}
        s3.copy_object(Bucket=Bucket, Key=file_key.replace("to_process", "processed"), CopySource=copy_source)
        s3.delete_object(Bucket=Bucket, Key=file_key)
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
