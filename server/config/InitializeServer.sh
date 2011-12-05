#!/bin/sh

### This script turns a fresh CentOS installation into an Elixys production server ###

# Make sure we're running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root."
   exit 1
fi

# Start in the root directory
cd /root

# Install git and do a pull
yum -y install git
git clone --depth 1 http://github.com/michaelvandam/elixys.git

# Create the root application directory
mkdir /opt/elixys

# Install, start and initialize MySQL
yum -y install mysql mysql-server apr-util-mysql
/sbin/service mysqld start
cd elixys/server/config
chmod 755 *.sh
./InitializeDatabase.sh
cd ../../..

# Make an application copy of the config directory
cp -R elixys/server/config /opt/elixys

# Initialize and make an application copy of the rtmpd directory
### Needs work!
chmod 711 elixys/server/rtmpd/crtmpserver
cp -R elixys/server/rtmpd /opt/elixys

# Install mod_wsgi
yum -y install mod_wsgi

# Install configobj for Python
wget http://www.voidspace.org.uk/downloads/configobj-4.7.2.zip
mkdir configobj
unzip -d configobj configobj-4.7.2.zip
cd configobj/configobj-4.7.2
python setup.py install
cd ../..
rm -rf configobj*

# Install RPyC for Python
wget http://downloads.sourceforge.net/project/rpyc/main/3.1.0/RPyC-3.1.0.zip
unzip RPyC-3.1.0.zip
cd RPyC-3.1.0
python setup.py install
cd ..
rm -rf RPyC-3.1.0*

# Install setuptools for Python
wget http://peak.telecommunity.com/dist/ez_setup.py
python ez_setup.py
rm -f ez_setup.py

# Install MySQL for Python
yum -y install python-devel mysql-devel
wget http://sourceforge.net/projects/mysql-python/files/mysql-python/1.2.3/MySQL-python-1.2.3.tar.gz/download
tar -xf MySQL-python-1.2.3.tar.gz
cd MySQL-python-1.2.3
python setup.py build
python setup.py install
cd ..
rm -rf MySQL-python-1.2.3*

# Set Apache and MySQL to start at boot
echo "service httpd start" >> /etc/rc.local
echo "service mysqld start" >> /etc/rc.local

# Initialize Apache directory tree
rm -rf /var/www/*
mkdir /var/www/adobepolicyfile
mkdir /var/www/http
mkdir /var/www/wsgi

# Create a directory where Apache has write permissions for Python Eggs 
mkdir /var/www/eggs
chmod 777 /var/www/eggs
chown apache:apache /var/www/eggs

# Install SELinux management tools and define the RPC port
yum -y install policycoreutils-python
semanage port -a -t http_port_t -p tcp 18862

# Install the Adobe policy module and file
cp elixys/server/config/adobepolicyfile/mod_adobe_crossdomainpolicy.so /usr/lib64/httpd/modules/
chmod 755 /usr/lib64/httpd/modules/mod_adobe_crossdomainpolicy.so
cp elixys/server/config/adobepolicyfile/crossdomain.xml /var/www/adobepolicyfile
chmod 444 /var/www/adobepolicyfile/crossdomain.xml

# Update the firewall settings
mv -f elixys/server/config/iptables /etc/sysconfig/
chcon --user=system_u --role=object_r --type=etc_t /etc/sysconfig/iptables
/sbin/service iptables restart

# Put shortcuts on the user's desktop
chmod 755 elixys/server/config/shortcuts/*.sh
cp elixys/server/config/shortcuts/* /home/$USER/Desktop

# Give all users the ability to run the update script as root
echo "ALL ALL=(ALL) NOPASSWD:/opt/elixys/config/UpdateServer.sh" >> /etc/sudoers

# Remove the git repository
rm -rf /root/elixys

# Run the update script to perform the initial pull of the source code
cd /home/$USER/Desktop
./UpdateServer.sh

