#Define dependencies
import requests 
import time
import pandas as pd

#Define custom classes to be used in the program
class MyException(Exception):
    pass

#Define variables
API_KEY = "YOUR_API_KEY"

api_url = "https://places.googleapis.com/v1/places:searchText"

print(api_url)

# JSON payload 
payload = { 
    "textQuery": "Nothing Bundt Cakes", 
    "pageSize": 0, 
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
    "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.priceLevel,places.reviews,nextPageToken" 
} 

try:
    # Make the POST request 
    response = requests.post(api_url, json=payload, headers=headers) 

    if response.status_code == 200:
        #Store the JSON response 
        res = response.json()
        nextPage = res.get('nextPageToken')
        #Perform mapping for corresponding columns to be used in the dataframe
        #1. Obtain the first and second level data from the JSON object
        df = pd.json_normalize(res["places"])
        print(f"The length of the call was {len(df)}.")
        print(f"Moving onto next page: {nextPage}.")

        # Generate a loop to iterate through all of the pages available for the data of interest
        while nextPage:
            # Introduce a pause before the next page is extracted
            time.sleep(5)
            # Update the next page to be extracted
            payload['pageToken'] = nextPage
            print(f"The payload is now: {payload}")
            # Store the JSON response
            response = requests.post(api_url, json=payload, headers=headers)

            if response.status_code == 200:
                res = response.json()
                nextPage = res.get('nextPageToken')
                print(f"The length of the call was {len(df)}.")
                print(f"Moving onto next page: {nextPage}")
                # Extract, store and append data onto a pandas dataframe
                df = pd.concat([df,pd.json_normalize(res["places"])], ignore_index = True)

            else:
                raise MyException()

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
    print(f"The feedback given is {response.content}")

