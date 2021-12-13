#!/bin/bash

for server in search01 search02 ; do
    rm -rf data/${server}
    mkdir -p data/${server}
    cd data/${server}
    scp -C "kis@${server}.epfl.ch:/var/www/vhosts/search.epfl.ch/logs/search-2012.epfl.ch_access.log.*" .
    gunzip *.gz
    cd ..
    cat ${server}/* > ${server}.log
    cd ..
    # scp -C kis@${server}.epfl.ch:/var/www/vhosts/search.epfl.ch/logs/search-2012.epfl.ch_access.log data/${server}.log
done
