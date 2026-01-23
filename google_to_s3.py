# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/
import json
import boto3
import requests
import pandas as pd
from botocore.exceptions import ClientError

class MyException(Exception):
    pass

def get_secret():

    secret_name = "YOUR_SECRET_MANAGER_SECRET"
    region_name = "YOUR_REGION_NAME"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']

    return secret

# Lambda execution code
def lambda_handler(event, context):
    api_url = "https://places.googleapis.com/v1/places:searchText"

    # JSON payload 
    payload = { 
        "textQuery": "Nothing Bundt Cakes", 
        "pageSize": 3, 
        "locationRestriction": { 
            "rectangle": { 
                # Southwest corner (continental US)
                "low": {
                    "latitude": 24.396308, 
                    "longitude": -125.0}, 
                # Northeast corner 
                "high": {
                    "latitude": 49.384358, 
                    "longitude": -66.93457} 
                } 
            } 
        } 

    # Headers used tied to the API URL
    headers = { 
        "Content-Type": "application/json", 
        "X-Goog-Api-Key": API_KEY, 
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.priceLevel,places.reviews" 
    } 

    try:
        # Make the POST request 
        response = requests.post(api_url, json=payload, headers=headers) 

        if response.status_code == 200:
            #Store the JSON response 
            res = response.json()
            #Perform mapping for corresponding columns to be used in the dataframe
            #1. Obtain the first and second level data from the JSON object
            df = pd.json_normalize(res["places"])
            #2. Retrieve the data from beyond the second level nest of JSON objects
            df_exp = df.explode("reviews").reset_index(drop=True)
            #3. Define a pandas dataframe for the flattened reviews
            revs_df = pd.json_normalize(df_exp["reviews"])
            #4. Combine the original dataframe with the newly created dataframe for the reviews data
            df = pd.concat([df_exp.drop(columns=["reviews"]), revs_df], axis = 1)
            #5. Filter for only US businesses
            df = df[df["formattedAddress"].str.contains("USA")].reset_index(drop=True)
            #6. Send to file
            df.to_csv("final_csv.csv")    

        else:
            raise MyException()

    except: 
        print(f"API request failed with status code: {response.status_code}")
