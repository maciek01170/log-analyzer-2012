#!/bin/bash

for server in search01 search02 ; do
    rm -rf data/$server/*.log*
    scp -C "kis@${server}.epfl.ch:/var/www/vhosts/search.epfl.ch/logs/search-2012.epfl.ch_access.log.202112*" data/${server}/
    gunzip data/${server}/*.gz
    cat data/${server}/*.log* > data/${server}.log
    # scp -C kis@${server}.epfl.ch:/var/www/vhosts/search.epfl.ch/logs/search-2012.epfl.ch_access.log data/${server}.log
done
