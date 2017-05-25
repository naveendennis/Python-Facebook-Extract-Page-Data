import requests
import configparser
import json


def load():
    config = configparser.ConfigParser()
    config.read('config.ini')
    config = config['facebook']
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--url',
                        type=str,
                        default=config['url'],
                        help='THe url that is present in the Facebook Graph API tool')
    parser.add_argument('--access_token',
                        type=str,
                        default=config['access_token'],
                        help='The access token used by the application')
    parser.add_argument('--method',
                        type=str,
                        default=config['method'],
                        help='Type of method used by request - get/post')
    parser.add_argument('--domain',
                        type=str,
                        default=config['domain'],
                        help='The starting portion of the "url" argument. Do not change this.')
    args = parser.parse_args()
    # access_token = get_access_token(args, config)
    return args, config


def format_date(datestring):
    return datestring[0: datestring.find('T')]


def extract_date(datestring):
    import datetime
    date_mentioned = datetime.datetime.strptime(datestring, "%Y-%m-%d").date()
    return date_mentioned


def get_all_posts(start_pointer, start_date, end_date):
    all_posts = list()

    while True:
        try:
            result = start_pointer['posts']['data']
        except KeyError:
            result = start_pointer['data']
        for each_status in result:
            date_string = each_status['created_time']
            date_mentioned = format_date(date_string)
            date_mentioned = extract_date(date_mentioned)
            if start_date < date_mentioned < end_date:
                all_posts.append(each_status)

        if date_mentioned < start_date:
            break
        try:
            url = start_pointer['posts']['paging']['next']
        except KeyError:
            url = start_pointer['paging']['next']
        response = requests.get(url)
        start_pointer = json.loads(response.text)
    return all_posts


def construct_url(args):
    return args.domain + args.url + '&' + 'access_token=' + args.access_token


def construct_json_for_page(all_posts, args):
    page_id = args.url.split('?')[0]
    result = dict()
    result['id']=page_id
    result['data']=all_posts
    with open('data/page_'+page_id, 'w') as f:
        json.dump(all_posts, f)


def main():
    args, config = load()
    start_date = extract_date(config['start_date'])
    end_date = extract_date(config['end_date'])
    url = construct_url(args)
    response = requests.get(url)
    start_pointer = json.loads(response.text)
    all_posts = get_all_posts(start_pointer, start_date, end_date)
    construct_json_for_page(all_posts, args)


if __name__ == '__main__':
    main()
