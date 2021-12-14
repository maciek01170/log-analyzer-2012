# analyze search-2012/search-api access logs and extract the stats about :
# - remote IPs
# - URI and current server
# - queries
#
# <search-2012 apache config>
# LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\" %{Host}i%U%q" with_serverAlias
# SetEnvIf Request_URI "^/cgi-bin/(.*)-check$" dontlog_serverAlias
# SetEnvIf Remote_Addr "^128.178.109.228$" dontlog_serverAlias
# SetEnvIf Remote_Addr "^128.178.209.209$" dontlog_serverAlias
# SetEnvIf Remote_Addr "^128.178.209.56$" dontlog_serverAlias
# CustomLog "/var/www/vhosts/search.epfl.ch/logs/search-2012.epfl.ch_access.log" with_serverAlias env=!dontlog_serverAlias
# </search-2012 apache config>
#
import glob
import os
import re
import apachelogs

from filters import ReFilter, DateFilter

# Log format from apache config
LOG_FORMAT = "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\" %{Host}i%U%q"


# parse all collected logs, returns the list of apahce log entries
def parse_logs(log_format):
    log_parser = apachelogs.LogParser(log_format)
    result = []
    folder_path = '../data/'
    for filename in glob.glob(os.path.join(folder_path, '*.log')):
        with open(filename, 'r') as fp:
            result += log_parser.parse_lines(fp)
    return result


# filters (list of REs):
# e_filter = exclusion, log entries will be excluded from further processing
# i_filter = inclusion, log entries will be included into further processing. Priority over e_filter!

filters = {
    # 'date': DateFilter(start_date='2021-10-12', end_date='2021-10-15'),
    'e_uri': None,  # ReFilter([r'\.epfl\.ch/(cgi-bin|js|styles|images)/', r'^(search-api|organigramme)']),
    'i_uri': None,  # ReFilter([r'^organigramme']),
    'e_rhost': None,
    'e_rhost_unused': ReFilter([
        r'^128.178.209.209',
        r'^128.178.209.56',
        r'^10.180.21.34',
        r'^128.178.109.228',
        r'^34.89.133.170',
        r'^128.178.166.36',
        r'^128.178.224.25[12]'
    ]),
    'i_rhost': None,
    'e_server': None,
    'e_filter_ununsed': ReFilter([
        r'^organigramme.epfl.ch',
        r'^search-api.epfl.ch',
        r'^search0[12].epfl.ch',
        r'^128.178.224.19[45]'
    ]),
    'i_server': None  # ReFilter(['^search-2012.epfl.ch$'])
}


# return True if the request is excluded from any e_filter and not included in any i_filter in filters
def excluded(keys):
    for cnt_key in keys:
        value = request[cnt_key]
        if ReFilter.matches(filters.get('e_' + cnt_key), value) and not ReFilter.matches(filters.get('i_' + cnt_key), value):
            return True
    return False


# counters titles and keys
cnt_keys_title = {
    'rhost': 'Remote host',
    'server': 'ServerAlias',
    'server_rhost': 'ServerAlias x Remote host',
    'uri': 'URI w/o QS',
    'uri_qs': 'Full URI'
}
cnt_keys = list(cnt_keys_title.keys())

# counters : key (from cnt_keys) -> {key: cnt from request}
cnt = {key: {} for key in cnt_keys}

# crt request
request = {}


# increment cnt for all keys
def inc(keys):
    for cnt_key in keys:
        if request.get(cnt_key) is not None:
            cnt[cnt_key][request[cnt_key]] = cnt[cnt_key].get(request[cnt_key], 0) + 1


# prints the list of cnts with given cnt_key:
#   fmt = format using item_key and item_value,
#   threshold = number of printed entries
def print_cnt(cnt_key, threshold=1, fmt=lambda item_key, value: f"{item_key:>15}: {value}"):
    def counter_iter():
        d = {k: v for k, v in cnt[cnt_key].items() if v > threshold}.items() if threshold > 1 else cnt[cnt_key].items()
        return enumerate(dict(sorted(d, key=lambda x: x[1], reverse=True)).items())

    print(f"\n* {cnt_keys_title[cnt_key]} details:")
    for idx, (item_key, value) in counter_iter():
        print(f"{idx+1:4}. " + fmt(item_key, value))


if __name__ == '__main__':
    nb_entries = 0 # number of non excluded entries
    logs = parse_logs(LOG_FORMAT)
    for entry in logs:
        if not DateFilter.between(filters.get('date'), entry.request_time):
            continue
        server = re.sub(r'^(.*).epfl.ch.*', r'\1.epfl.ch', entry.request_uri)
        server = re.sub(r'^([a-zA-Z0-9_\-]+.epfl.ch){1}?.*$', r'\1', server, re.ASCII)
        server = re.sub(r'/$', '', server)
        request = {
            'server': server,
            'rhost': entry.remote_host,
            'query': entry.request_query or '',
            'server_rhost': server + "_" + entry.remote_host,
        }
        uri = re.sub(r';jsessionid=[A-Z0-9]+', '', entry.request_line.split(' ')[1].split('?')[0])
        request['uri'] = request['server'] + uri
        if request['query']:
            request['uri_qs'] = request['uri'] + request['query']

        if excluded(['server', 'rhost', 'uri']):
            continue

        inc(['server', 'rhost', 'uri', 'uri_qs', 'server_rhost'])
        nb_entries += 1

    print(f"# entries: {nb_entries}/{len(logs)}")
    for cnt_key in cnt_keys:
        print(f"# {cnt_key}: {len(cnt[cnt_key])} ({cnt_keys_title[cnt_key]})")

    print_cnt("server")
    print_cnt("rhost")
    print_cnt("server_rhost")
    print_cnt("uri", fmt=lambda item_key, value: f"https://{item_key:<40}: {value}")
    print_cnt("uri_qs", fmt=lambda item_key, value: f"https://{item_key:<80}: {value}")

    # exit(255)
