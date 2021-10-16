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

LOG_FORMAT = "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\" %{Host}i%U%q"


# parse logs using apachelogs
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
    'date': DateFilter(start_date='2021-10-12', end_date='2021-10-15'),
    'e_uri': ReFilter([r'\.epfl\.ch/(cgi-bin|js|styles|images)/', r'^(search-api|organigramme)']),
    'i_uri': None,  # ReFilter([r'^organigramme']),
    'e_rhost': ReFilter(['(34.89.133.170|128.178.209.56|128.178.209.209|128.178.109.228)']),
    'i_rhost': None,
    'e_server': ReFilter(['^.*.epfl.ch$']),
    'i_server': ReFilter(['^search-2012.epfl.ch$'])
}


def excluded(keys):
    for key in keys:
        value = request[key]
        if ReFilter.matches(filters['e_' + key], value) and not ReFilter.matches(filters['i_' + key], value):
            return True
        return False


cnt_keys = ['rhost', 'server', 'uri', 'uri_qs']
cnt = {key: {} for key in cnt_keys}
request = {}


def inc(keys):
    for key in keys:
        if request.get(key) is not None:
            cnt[key][request[key]] = cnt[key].get(request[key], 0) + 1


def counter_iter(key, threshold=1):
    d = {k: v for k, v in cnt[key].items() if v > threshold}.items() if threshold > 1 else cnt[key].items()
    return enumerate(dict(sorted(d, key=lambda x: x[1], reverse=True)).items())


if __name__ == '__main__':
    nb_entries = 0
    logs = parse_logs(LOG_FORMAT)
    for entry in logs:
        if not DateFilter.between(filters['date'], entry.request_time):
            continue
        request = {
            'server': re.sub('^(.*).epfl.ch.*', r'\1.epfl.ch', entry.request_uri),
            'rhost': entry.remote_host,
            'query': entry.request_query or ''
        }
        request['uri'] = request['server'] + entry.request_line.split(' ')[1].split('?')[0]
        if request['query']:
            request['uri_qs'] = request['uri'] + request['query']

        if excluded(['server', 'rhost', 'uri']):
            continue
        inc(['server', 'rhost', 'uri', 'uri_qs'])
        nb_entries += 1

    print(f"# entries: {nb_entries}/{len(logs)}")
    for key in cnt_keys:
        print(f"# {key}: {len(cnt[key])}")

    print(f"Server details: ")
    for idx, (server, value) in counter_iter('server'):
        print(f"{idx+1:4}. {server:>15}: {value}")
    print(f"Remote host details: ")
    for idx, (ip, value) in counter_iter('rhost'):
        print(f"{idx+1:4}. {ip:>15}: {value}")
    print(f"URI details (> 10)")
    for idx, (uri, value) in counter_iter('uri'):
        print(f"{idx+1:4}. https://{uri:<40}: {value}")
    exit(255)
    print(f"Full URI details")
    for idx, (uri, value) in counter_iter('uri_qs'):
        print(f"{idx+1:4}. https://{uri:<80}: {value}")
