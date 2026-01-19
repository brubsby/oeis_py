#!/bin/bash

Q="-2 -1 1 2"
P="1 2 3 4 5 6 7 8 9 10 11 12"

for q in ${Q}; do
    for p in ${P}; do
        u=u${p}.${q}.dat
        echo "$(date +'%Y-%m-%d %H:%M:%S') Restoring ${u} using backup"
        cp "${u}" ..
        #sleep 300
        v=v${p}.${q}.dat
        echo "$(date +'%Y-%m-%d %H:%M:%S') Restoring ${v} using backup"
        cp "${v}" ..
        #sleep 300
    done
done