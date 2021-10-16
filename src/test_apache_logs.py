# analyze search-2012/search-api access logs and extract the stats about :
# - remote IPs
# - URI and current server
# - queries
#
# search-2012 apache config
# LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\" %{Host}i%U%q" with_serverAlias
# SetEnvIf Request_URI "^/cgi-bin/(.*)-check$" dontlog_serverAlias
# SetEnvIf Remote_Addr "^128.178.109.228$" dontlog_serverAlias
# SetEnvIf Remote_Addr "^128.178.209.209$" dontlog_serverAlias
# SetEnvIf Remote_Addr "^128.178.209.56$" dontlog_serverAlias
# CustomLog "/var/www/vhosts/search.epfl.ch/logs/search-2012.epfl.ch_access.log" with_serverAlias env=!dontlog_serverAlias

import apachelogs
import datetime
import os
import glob
from filters import ReFilter

LOG_FORMAT = "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\" %{Host}i%U%q"


def parse_logs(log_format):
    log_parser = apachelogs.LogParser(LOG_FORMAT)
    result = []
    folder_path = '../data/'
    for filename in glob.glob(os.path.join(folder_path, '*.log')):
        with open(filename, 'r') as fp:
            result += log_parser.parse_lines(fp)
    return result


def inc(d, key):
    d[key] = d.get(key, 0) + 1


# filters
START_DATE = '2012-10-12'
start_date = datetime.datetime.strptime(START_DATE, '%Y-%m-%d').date()
e_uri_filter = ReFilter([r'\.epfl\.ch/(cgi-bin|js|styles|images)/', r'^(search-api|organigramme)'])
i_uri_filter = None # ReFilter([r'^organigramme'])
e_host_filter = ReFilter(['(34.89.133.170|128.178.209.56|128.178.209.209|128.178.109.228)'])

if __name__ == '__main__':
    ips = {}
    uris = {}
    uris_qs = {}
    cnt = 0
    logs = parse_logs(LOG_FORMAT)
    for entry in logs:
        if start_date > entry.request_time.date():
            continue
        host = entry.remote_host
        uri = entry.request_uri
        query = entry.request_query or ''
        if e_host_filter and e_host_filter.matches(host):
            continue
        if e_uri_filter and e_uri_filter.matches(uri)  and not (i_uri_filter and i_uri_filter.matches(uri)):
            continue
        inc(ips, host)
        inc(uris, uri)
        if query:
            inc(uris_qs, uri + query)
        cnt += 1

    print(f"# entries: {cnt}/{len(logs)}")
    print(f"# remote hosts: {len(ips)}")
    print(f"# URIs: {len(uris)}")
    print(f"# URIs + QS: {len(uris_qs)}")
    print(f"Remote host details: ")
    for idx, (ip, value) in enumerate(dict(sorted(ips.items(), key=lambda x: x[1], reverse=True)).items()):
        print(f"{idx+1:4}. {ip:>15}: {value}")
    print(f"URI details")
    for idx, (uri, value) in enumerate(dict(sorted(uris.items(), key=lambda x: x[1], reverse=True)).items()):
        print(f"{idx+1:4}. https://{uri:<40}: {value}")
    print(f"Full URI details")
    for idx, (uri, value) in enumerate(dict(sorted(uris_qs.items(), key=lambda x: x[1], reverse=True)).items()):
        print(f"{idx+1:4}. https://{uri:<80}: {value}")
