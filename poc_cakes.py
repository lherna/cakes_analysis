import requests 
import pandas as pd

class MyException(Exception):
    pass

API_KEY = "API_KEY"

api_url = "https://places.googleapis.com/v1/places:searchText"

print(api_url)

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

#print(f"payload is {payload}")

# Headers 
headers = { 
    "Content-Type": "application/json", 
    "X-Goog-Api-Key": API_KEY, 
    "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.priceLevel,places.reviews" 
} 

#print(f"headers are {headers}")

try:
    # Make the POST request 
    response = requests.post(api_url, json=payload, headers=headers) 

    if response.status_code == 200:
        #Store the JSON response 
        res = response.json()
        #Perform mapping for corresponding columns to be used in the dataframe
        df = pd.json_normalize(res["places"])
        df_exp = df.explode("reviews").reset_index(drop=True)
        revs_df = pd.json_normalize(df_exp["reviews"])
        df = pd.concat([df_exp.drop(columns=["reviews"]), revs_df], axis = 1)
        #Filter for only US businesses
        df = df[df["formattedAddress"].str.contains("USA")].reset_index(drop=True)
        df.to_csv("final_csv.csv")    

    else:
        raise MyException()

except: 
    print(f"API request failed with status code: {response.status_code}")
