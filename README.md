# Python-Facebook-Extract-Page-Data

Given the partial URL entered into graph API of the format 

    15704546335/posts?after=Q2c4U1pXNTBYM0YxWlhKNVgzTjBiM0o1WDJsa0R5QXhOVGN3TkRVME5qTXpOVHN4TURFMU5USTFOamszT1RRMk1UTXpOanM3TkE4TVlYQnBYM04wYjNKNVgybGtEeDB4TlRjd05EVTBOak16TlY4eE1ERTFOVEkxTmprM09UUTJNVE16Tmc4RWRHbHRaUVpZAMjdqSEFRPT0ZD&fields=message,id,created_time&limit=25
    
The app will fetch all the posts between the `start date` and the `end date` provided.    

## Command Line Arguments

The following command-line parameters are used :

`--start_date` provide the start date

`--end_date` provide the end date

`--access_token` manually pass the access token

`--url` the partial url typed into the graph API explorer

The access token, url and other properties can be modified by editing the `config.ini` file directly.

## Usage

    python3 facebook_requests.py --start_date 2016-05-22 --end_date 2017-01-01
