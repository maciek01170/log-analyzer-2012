import apachelogs
import re
import datetime

# apache config
# LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\" %{Host}i%U%q" with_serverAlias
# SetEnvIf Request_URI "^/cgi-bin/(.*)-check$" dontlog_serverAlias
# SetEnvIf Remote_Addr "^128.178.109.228$" dontlog_serverAlias
# SetEnvIf Remote_Addr "^128.178.209.209$" dontlog_serverAlias
# SetEnvIf Remote_Addr "^128.178.209.56$" dontlog_serverAlias
# CustomLog "/var/www/vhosts/search.epfl.ch/logs/search-2012.epfl.ch_access.log" with_serverAlias env=!dontlog_serverAlias
LOG_FORMAT = "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\" %{Host}i%U%q"
parser = apachelogs.LogParser(LOG_FORMAT)

if __name__ == '__main__':
    date_filter = datetime.date(2021, 10, 13, tzinfo=datetime.timedelta(7200))
    ips = {}
    uris = {}
    cnt = 0
    with open("../data/search01.log", "r") as fp:
        for entry in parser.parse_lines(fp):
            request_uri, request_query = entry.request_uri, '?' + entry.request_query if entry.request_query else ''
            if not re.search(r'^search-2012', request_uri) or re.search(r'/styles/', request_uri):
                continue
            # print(f"{entry.remote_host} - https://{request_uri}{request_query}")
            ips[entry.remote_host] = ips.get(entry.remote_host, 0) + 1
            uris[request_uri] = uris.get(request_uri, 0) + 1
            cnt += 1

    print(f"# entries: {cnt}")
    print(f"# remote hosts: {len(ips)}")
    print(f"# URIs: {len(uris)}")
    print(f"Remote host details: ")
    for idx, (ip, value) in enumerate(dict(sorted(ips.items(), key=lambda x: x[1])).items()):
        print(f"{idx+1:4}. {ip:>15}: {value}")
