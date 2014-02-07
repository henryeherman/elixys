#!/usr/bin/env bash

sudo apt-get -o -y -q DPkg::Options::="--force-confmiss" --reinstall install crtmpserver
sudo apt-get -o -y -q DPkg::Options::="--force-confmiss" --reinstall install supervisor 

patch /etc/init.d/supervisor < supervisor.patch

ln -s /opt/elixys/config/elixyssupervisord.conf  \ 
        /etc/supervisor/conf.d

service crtmpserver restart
service supervisor restart
