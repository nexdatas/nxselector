#!/usr/bin/env bash


echo "install pixi"
docker exec  ndts /bin/bash -c 'curl -fsSL https://pixi.sh/install.sh | sh ; export PATH=/var/lib/tango/.pixi/bin:$PATH ; cp .github/workflows/pixi/pixi.toml . ; pixi shell-hook  > .sh.sh ; source .sh.sh ; pixi add   numpy "pytango=10.1.4" setuptools pip wheel argcomplete lxml pytz pyyaml  python-dateutil pninexus fabio h5py matplotlib-base blissdata pytest docutils nxsconfigserver nxswriter pymysql nxstools pymysql sardana  nxsrecselector taurus nxsconfigserver-db'

docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=root\npassword=rootpw" > /root/.my.cnf'
# docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=tango\nhost=localhost\npassword=rootpw" > /var/lib/tango/.my.cnf'
docker exec  --user root ndts /bin/bash -c 'echo -e "[client]\nuser=tango\nhost=localhost\npassword=rootpw" > /home/tango/.my.cnf'
docker exec  --user root ndts chown -R tango:tango /home/tango/.my.cnf
docker exec  --user root ndts chown -R tango:tango /var/lib/tango/.my.cnf

docker exec  --user root ndts /usr/bin/mysql -e 'create database nxsconfig'
docker exec  --user root ndts /bin/bash -c 'source .sh.sh ; /usr/bin/mysql nxsconfig < "$CONDA_PREFIX"/share/nxsconfigserver/mysql_create.sql'
docker exec  --user root ndts /usr/bin/mysql -e 'GRANT ALL PRIVILEGES ON nxsconfig.* TO "tango"@"%" identified by "rootpw"'
docker exec  --user root ndts /usr/bin/mysql -e 'GRANT ALL PRIVILEGES ON nxsconfig.* TO "tango"@"localhost" identified by "rootpw"'
docker exec  --user root ndts /usr/bin/mysql -e 'FLUSH PRIVILEGES'

# # # create nxsconfig database
# docker exec  ndts /bin/bash -c 'source .sh.sh ;  echo "export MY_PREFIX=$CONDA_PREFIX" > /home/tango/.menv'
# docker exec  --user root ndts /bin/bash -c 'source /home/tango/.menv ; export MYSQL_PASSWORD="rootpw" ; "$MY_PREFIX"/bin/create_nxsconfig_db -x -d=nxsonfig -u=tango -p="$MY_PREFIX"'

echo "run nxselector tests"
docker exec  ndts /bin/bash -c 'source .sh.sh ;  echo "export MYTANGO_PREFIX=$CONDA_PREFIX/bin" > /home/tango/.env ;   python -m pip install . -vv --no-deps --no-build-isolation ;  QT_QPA_PLATFORM=offscreen python test'

ERROR=$?
if [ $ERROR -ne "0" ]
then
    echo "ERROR "$ERROR
    exit 255
fi
