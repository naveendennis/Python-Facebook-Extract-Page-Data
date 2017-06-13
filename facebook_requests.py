import requests
import configparser
import json
import string
import pathlib
import os

config = configparser.ConfigParser()
config.read(os.path.join('properties', 'config.ini'))


def load():
    global config
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--url',
                        type=str,
                        default=config['facebook']['url'],
                        help='THe url that is present in the Facebook Graph API tool')
    parser.add_argument('--access_token',
                        type=str,
                        default=config['facebook']['access_token'],
                        help='The access token used by the application')
    parser.add_argument('--method',
                        type=str,
                        default=config['facebook']['method'],
                        help='Type of method used by request - get/post')
    parser.add_argument('--domain',
                        type=str,
                        default=config['facebook']['domain'],
                        help='The starting portion of the "url" argument. Do not change this.')
    args = parser.parse_args()
    # access_token = get_access_token(args, config)
    return args


def get_new_access_token(config):
    refresh_token_url = config['facebook']['domain'] + \
                        'oauth/access_token?' + \
                        'grant_type=fb_exchange_token&' + \
                        'client_id=' + config['facebook']['client_id'] + '&' + \
                        'client_secret=' + config['facebook']['client_secret'] + '&' + \
                        'fb_exchange_token=' + config['facebook']['access_token']
    new_access_token = requests.get(refresh_token_url)
    return json.loads(new_access_token.text)['access_token']


def format_date(datestring):
    return datestring[0: datestring.find('T')]


def extract_date(datestring):
    import datetime
    date_mentioned = datetime.datetime.strptime(datestring, "%Y-%m-%d").date()
    return date_mentioned


def file_exists(path):
    path = pathlib.Path(path)
    return path.is_file()


def get_response(url):
    global config
    access_config = configparser.ConfigParser()
    page_id = config['facebook']['url'].split('?')[0].split('/')[0]
    access_token_fn = 'properties/access_token'+page_id+'.ini'

    if file_exists(access_token_fn):
        access_config.read(access_token_fn)
        config['facebook']['access_token'] = access_config['facebook']['access_token']
    else:
        access_config.add_section('facebook')
        access_config.set('facebook', 'access_token', config['facebook']['access_token'])

    config.set('facebook', 'access_token', get_new_access_token(config))
    with open(access_token_fn, 'w') as f:
        access_config.write(f)
    response = requests.get(url + '&access_token=' + access_config['facebook']['access_token'])
    return response


def reconnect(url):
    global config
    counter = 0
    response = get_response(url)
    while response.status_code != 200:
        counter += 1
        response = get_response(url)
        if counter == int(config['facebook']['reconnect']):
            return None
    return response


def get_all_posts(args, start_date, end_date):
    global config
    url = construct_url(domain=args.domain,
                        url=args.url,
                        access_token=args.access_token)
    response = get_response(url)
    start_pointer = json.loads(response.text)
    config['facebook']['access_token'] = args.access_token
    return get_them_all(args, start_date, end_date, start_pointer)


def is_in_topic(message):
    global config
    result = False
    translator = str.maketrans(' ', ' ', string.punctuation)
    considered_tokens = config['facebook']['searchTokens'].split(' ')
    tokens_in_each_status = message.strip().translate(translator).lower().split(' ')
    for each_considered_token in considered_tokens:
        if each_considered_token in tokens_in_each_status:
            result = True
            break
    return result


def get_them_all(args, start_date, end_date, start_pointer, has_comment=True):

    global config
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
                    try:
                        if not is_in_topic(each_status['message']):
                            continue
                        else:
                            each_status['comments'] = get_them_all(args, start_date, end_date,
                                                                   each_status['comments'],
                                                                   has_comment=False)
                    except KeyError:
                        continue

                all_posts.append(each_status)
            else:
                break

        if date_mentioned < start_date:
            break
        try:
            url = start_pointer['paging']['next']
        except KeyError:
            break
        response = reconnect(url)
        if response is None:
            break
        start_pointer = json.loads(response.text)

    return all_posts


def construct_url(domain, url, access_token):
    return domain + url + '&' + 'access_token=' + access_token


def construct_json_for_page(all_posts, args):
    global config
    page_id = args.url.split('?')[0].split('/')[0]
    result = dict()
    result['id'] = page_id
    result['data'] = all_posts
    with open(os.path.join(config['facebook']['report_directory'], config['facebook']['report_append_fvalue']) + page_id, 'w') as f:
        json.dump(result, f)


def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def main():
    args = load()
    start_date = extract_date(config['facebook']['start_date'])
    end_date = extract_date(config['facebook']['end_date'])
    all_posts = get_all_posts(args, start_date, end_date)
    construct_json_for_page(all_posts, args)


if __name__ == '__main__':
    make_dir(config['facebook']['properties_directory'])
    make_dir(config['facebook']['data_directory'])
    import timeit
    start_time = timeit.default_timer()
    main()
    elapsed_time = timeit.default_timer() - start_time
    print('elapsed time :', elapsed_time)
