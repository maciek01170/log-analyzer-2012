#!/bin/bash

for server in search01 search02 ; do
    scp kis@${server}.epfl.ch:/var/www/vhosts/search.epfl.ch/logs/search-2012.epfl.ch_access.log data/${server}.log
done
