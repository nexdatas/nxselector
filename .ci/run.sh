#!/usr/bin/env bash

if [[ $1 == "2" ]]; then
    echo "run python-nxselector"
    docker exec  ndts python test
else
    echo "run python3-nxselector"
    docker exec  ndts python3 test
fi
if [ "$?" != "0" ]; then exit 255; fi
