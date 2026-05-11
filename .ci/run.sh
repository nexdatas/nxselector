#!/usr/bin/env bash

if [[ $1 == "2" ]]; then
    echo "run python-nxselector"
    docker exec  ndts python test
else
    echo "run python3-nxselector"
    docker exec  ndts python3 test
fi
ERR=$?

echo "ERROR: "$ERR

if [ $ERR != 0 ]; then
    if [ $ERR != 139 ]; then
	exit $ERR;
    fi
fi
