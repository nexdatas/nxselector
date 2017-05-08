FROM debian:stretch

MAINTAINER DESY, Jan Kotanski <jankotan@gmail.com>

RUN apt-get -qq update
RUN apt-get -qq install -y software-properties-common curl coreutils gnupg gnupg2 gnupg1 procps apt-utils
RUN add-apt-repository "deb http://repos.pni-hdri.de/apt/debian stretch main" -y
RUN curl http://repos.pni-hdri.de/debian_repo.pub.gpg | apt-key add -
RUN apt-get -qq update
RUN apt-get -qq -y upgrade
RUN apt-get -qq install -y default-mysql-client
# RUN apt-get -qq install -y  python-pni
RUN apt-get -qq install -y python-h5py
RUN apt-get -qq install -y python-sphinx
RUN apt-get -qq install -y apt-utils debconf-utils net-tools
# RUN apt-get -qq install -y build-essential cmake
RUN apt-get -qq install -y omniidl libomniorb4-dev libcos4-dev libomnithread3-dev libzmq3-dev
RUN useradd -ms /bin/bash tango
RUN  /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "mysql-server mysql-server/root_password password rootpw"'
RUN  /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "mysql-server mysql-server/root_password_again password rootpw"'
RUN  /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "mariadb-server mysql-server/root_password password rootpw"'
RUN  /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "mariadb-server mysql-server/root_password_again password rootpw"'
RUN  /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-get-selections |grep mysql '
RUN apt-get -qq install -y default-mysql-server adduser
RUN  /bin/bash -c 'sleep 10'
RUN /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "tango-db tango-db/db/app-user string tango"'
RUN /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "tango-db tango-db/mysql/app-pass	password rootpw"'
RUN /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "tango-db tango-db/mysql/admin-pass password rootpw"'
RUN /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "tango-db tango-db/password-confirm password rootpw"'
RUN /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "tango-db tango-db/app-password-confirm password rootpw"'
RUN /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "nxsconfigserver-db nxsconfigserver-db/mysql/app-pass password rootpw"'
RUN /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "nxsconfigserver-db nxsconfigserver-db/mysql/admin-pass password rootpw"'
RUN /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "nxsconfigserver-db nxsconfigserver-db/app-password-confirm password rootpw"'
RUN /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "nxsconfigserver-db nxsconfigserver-db/db/app-user string tango"'

ENV PKG_CONFIG_PATH=/home/tango/lib/pkgconfig
USER tango
WORKDIR /home/tango

