import requests
import configparser
import json
import string


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


def get_new_access_token(config):
    refresh_token_url = config['domain'] + \
                        'oauth/access_token?' + \
                        'grant_type=fb_exchange_token&' + \
                        'client_id=' + config['client_id'] + '&' + \
                        'client_secret=' + config['client_secret'] + '&' + \
                        'fb_exchange_token=' + config['access_token']
    new_access_token = requests.get(refresh_token_url)
    return json.loads(new_access_token.text)['access_token']


def format_date(datestring):
    return datestring[0: datestring.find('T')]


def extract_date(datestring):
    import datetime
    date_mentioned = datetime.datetime.strptime(datestring, "%Y-%m-%d").date()
    return date_mentioned


def get_response(url):
    config = configparser.ConfigParser()
    config.read('config.ini')
    config.set('facebook', 'access_token', get_new_access_token(config['facebook']))
    with open('config.ini', 'w') as f:
        config.write(f)
    response = requests.get(url + '&access_token=' + config['facebook']['access_token'])
    return response


def get_all_posts(args, config, start_date, end_date):
    url = construct_url(domain=args.domain,
                        url=args.url,
                        access_token=args.access_token)
    response = get_response(url)
    start_pointer = json.loads(response.text)
    config['access_token'] = args.access_token
    return get_them_all(args, config, start_date, end_date, start_pointer)


def is_in_topic(message, config):
    result = False
    translator = str.maketrans(' ', ' ', string.punctuation)
    considered_tokens = config['searchTokens'].split(' ')
    tokens_in_each_status = message.strip().translate(table=translator).lower().split(' ')
    for each_considered_token in considered_tokens:
        if each_considered_token in tokens_in_each_status:
            result = True
            break
    return result


def get_them_all(args, config, start_date, end_date, start_pointer, has_comment=True):

    all_posts = list()
    while True:
        try:
            result = start_pointer['data']
        except KeyError:
            break
        for each_status in result:
            date_string = each_status['created_time']
            date_mentioned = format_date(date_string)
            date_mentioned = extract_date(date_mentioned)
            if start_date < date_mentioned < end_date:
                if has_comment:
                    if not is_in_topic(each_status['message'], config):
                        continue

                    each_status['comments'] = get_them_all(args, config, start_date, end_date,
                                                           each_status['comments'],
                                                           has_comment=False)

                all_posts.append(each_status)
            else:
                break

        if date_mentioned < start_date:
            break
        try:
            url = start_pointer['paging']['next']
        except KeyError:
            break
        response = get_response(url)
        while response.status_code != 200:
            response = get_response(url)
        start_pointer = json.loads(response.text)

    return all_posts


def construct_url(domain, url, access_token):
    return domain + url + '&' + 'access_token=' + access_token


def construct_json_for_page(all_posts, args):
    page_id = args.url.split('?')[0].split('/')[0]
    result = dict()
    result['id'] = page_id
    result['data'] = all_posts
    with open('data/page_comments_' + page_id, 'w') as f:
        json.dump(result, f)


def main():
    args, config = load()
    start_date = extract_date(config['start_date'])
    end_date = extract_date(config['end_date'])
    all_posts = get_all_posts(args, config, start_date, end_date)
    construct_json_for_page(all_posts, args)


if __name__ == '__main__':
    main()
