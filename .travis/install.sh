#!/usr/bin/env bash

# workaround for incomatibility of default ubuntu 16.04 and tango configuration
if [[ $1 == "ubuntu16.04" ]]; then
    docker exec -it --user root ndts sed -i "s/\[mysqld\]/\[mysqld\]\nsql_mode = NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION/g" /etc/mysql/mysql.conf.d/mysqld.cnf
fi
if [ $1 = "ubuntu20.04" ]; then
    docker exec -it --user root ndts sed -i "s/\[mysql\]/\[mysqld\]\nsql_mode = NO_ZERO_IN_DATE,NO_ENGINE_SUBSTITUTION\ncharacter_set_server=latin1\ncollation_server=latin1_swedish_ci\n\[mysql\]/g" /etc/mysql/mysql.conf.d/mysql.cnf
fi

echo "restart mysql"
if [[ $1 == "debian9" ]]; then
    # workaround for a bug in debian9, i.e. starting mysql hangs
    docker exec -it --user root ndts service mysql stop
    docker exec -it --user root ndts /bin/sh -c '$(service mysql start &) && sleep 30'
else
    docker exec -it --user root ndts service mysql restart
fi

docker exec -it --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y   tango-db tango-common; sleep 10'
if [ "$?" -ne "0" ]
then
    exit -1
fi
echo "install tango servers"
docker exec -it --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get -qq install -y  tango-starter tango-test liblog4j1.2-java git'
if [ "$?" -ne "0" ]
then
    exit -1
fi

docker exec -it --user root ndts service tango-db restart
docker exec -it --user root ndts service tango-starter restart


if [[ $2 = "2" ]]; then
    echo "install python-pytango"
    docker exec -it --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y   python-pytango python-h5py  python-qtpy python-click git python-itango python-pint'
else
    echo "install python3-pytango"
    if [[ $1 == "debian9" ]]; then
	docker exec -it --user root ndts /bin/sh -c 'git clone https://github.com/hgrecco/pint pint-src; cd pint-src'
	docker exec -it --user root ndts /bin/sh -c 'cd pint-src; git checkout tags/0.8.1 -b b0.8.1; python3 setup.py install'
	# docker exec -it --user root ndts /bin/sh -c 'cd taurus-src; git checkout; python3 setup.py install'
    fi
    if [ $1 = "ubuntu20.04" ]; then
	docker exec -it --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get install -y git python3-six python3-numpy graphviz python3-sphinx g++ build-essential python3-dev pkg-config python3-all-dev  python3-setuptools libtango-dev python3-setuptools python3-tango python3-tz python3-enum34 python3-itango; apt-get -qq install -y nxsconfigserver-db; sleep 10'
    else
	docker exec -it --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get install -y git python3-six python3-numpy graphviz python3-sphinx g++ build-essential python3-dev pkg-config python3-all-dev  python3-setuptools libtango-dev python3-setuptools python3-pytango python3-tz python3-enum34 python3-itango; apt-get -qq install -y nxsconfigserver-db; sleep 10'
    fi
    docker exec -it --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get install -y libboost-python-dev libboost-dev python3-h5py python3-qtpy  python3-click python3-setuptools  python3-pint'
    if [[ $1 = "debian10" ]]; then
	echo " "
    elif [[ $1 == "ubuntu20.04" ]]; then
	echo " "
    else
	docker exec -it --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get install -y libtango-dev python3-dev'
	docker exec -it --user root ndts /bin/sh -c 'git clone https://github.com/tango-controls/pytango pytango; cd pytango; git checkout tags/v9.2.5 -b b9.2.5'
	docker exec -it --user root ndts /bin/sh -c 'cd pytango; python3 setup.py install'
    fi
fi
if [ "$?" -ne "0" ]
then
    exit -1
fi

echo "install qt5"
docker exec -it --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get -qq install -y  qtbase5-dev-tools qt5-default'
if [ "$?" -ne "0" ]
then
    exit -1
fi

if [[ $1 == "debian8" ]]; then
    if [[ $2 == "3" ]]; then
	echo "install python3-mysqldb"
	docker exec -it --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get install -y -t=jessie-backports  python3-mysqldb'
    fi
fi

if [[ $2 == "2" ]]; then
    echo "install sardana, taurus and nexdatas"
    docker exec -it --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get -qq install -y  nxsconfigserver-db; sleep 10; apt-get -qq install -y python-nxsconfigserver python-nxswriter python-nxstools python-nxsrecselector  python-setuptools'
    if [[ $1 == "debian10" ]]; then
	docker exec -it --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get -qq install -y python-taurus python-sardana'
    elif [[ $1 == "ubuntu20.04" ]]; then
	docker exec -it --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get -qq install -y python-taurus python-sardana'
    else
	docker exec -it --user root ndts /bin/sh -c 'git clone https://github.com/taurus-org/taurus taurus-src; cd taurus-src'
	docker exec -it --user root ndts /bin/sh -c 'cd taurus-src; git checkout tags/4.6.1 -b b4.6.1; python3 setup.py install'
	docker exec -it --user root ndts /bin/sh -c 'git clone https://github.com/sardana-org/sardana sardana-src; cd sardana-src'
	docker exec -it --user root ndts /bin/sh -c 'cd sardana-src; git checkout tags/2.8.4 -b b2.8.4; python setup.py install'
    fi
else
    echo "install sardana, taurus and nexdatas"
    docker exec -it --user root ndts /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get install -y  nxsconfigserver-db; sleep 10; apt-get -qq install -y python3-nxsconfigserver python3-nxswriter python3-nxstools python3-nxsrecselector python3-setuptools'
    docker exec -it --user root ndts /bin/sh -c 'git clone https://github.com/taurus-org/taurus taurus-src; cd taurus-src'
    docker exec -it --user root ndts /bin/sh -c 'cd taurus-src; python3 setup.py install'
    docker exec -it --user root ndts /bin/sh -c 'git clone https://github.com/sardana-org/sardana sardana-src; cd sardana-src'
    docker exec -it --user root ndts /bin/sh -c 'cd sardana-src; python3 setup.py install'
fi
if [ "$?" -ne "0" ]
then
    exit -1
fi

if [[ $2 == "2" ]]; then
    echo "install nxselector"
    docker exec -it --user root ndts python setup.py -q install
else
    echo "install nxselector3"
    docker exec -it --user root ndts python3 setup.py -q install
fi
if [ "$?" -ne "0" ]
then
    exit -1
fi

docker exec -it --user root ndts chown -R tango:tango .
