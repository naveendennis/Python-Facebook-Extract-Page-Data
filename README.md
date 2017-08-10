# Python-Facebook-Extract-Page-Data

Given the partial URL entered into graph API of the format 

    <page-id>/posts?fields=message,created_time,id,attachments{url},from,to,comments{from,message,created_time,id}

## Command Line Arguments

The following command-line parameters are used :

`--access_token` manually pass the access token

`--url` the partial url typed into the graph API explorer

The access token, url and other properties can be modified by editing the `config.ini` file directly. `(Recommended)`

`start_date` and `end_date` fields in `config.ini` is used to determine the range of posts extracted by the program

## Usage

    python3 facebook_requests.py
