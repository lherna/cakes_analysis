# Cakes Analysis

This project encompasses the workthrough of connecting to the google API, processing the data through AWS and making it available in an S3 bucket that is used as a datalake sample. Once the data is available in S3, it is pushed onto Snowflake where it is then leveraged by Tableau to perform some analysis on the data that can give us some insights. 

## Proof-of-concept development to ensure that the API can be connected to and data can be extracted.

As we can see from the file named poc_cakes.py, the code goes through the API connection and leverages pandas dataframes to make the data available in a data friendly format.

To run the poc_cakes.py file, we simply need to run it with the following command:

python poc_cakes.py 

Which will result in a file being created with the processed output. 
