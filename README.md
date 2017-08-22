# Python-Facebook-Extract-Page-Data

## Command Line Arguments

The following command-line parameters are used :

`--access_token` manually pass the access token

`--url` the partial url typed into the graph API explorer

`--start_date` date from when the posts are to be extracted

`--end_date`end date to which the posts are to be extracted

`--page_id` The FacebookID of the Page from which data is to be extracted.

The access token, url and other properties can be modified by editing the `config.ini` file directly. `(Recommended)`

`start_date` and `end_date` fields in `config.ini` is used to determine the range of posts extracted by the program

## Usage

    python3 facebook_requests.py --start_date 2016-05-22 --end_date 2017-01-01 --page_id SeventhAnomaly
    
    (Or)
    
    python3 facebook_request.py
    
Default property values are in `properties/config.ini`
