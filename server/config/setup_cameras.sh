#!/usr/bin/env bash

sudo apt-get -o -y -q DPkg::Options::="--force-confmiss" --reinstall install crtmpserver
sudo apt-get -o -y -q DPkg::Options::="--force-confmiss" --reinstall install supervisor 

sudo patch /etc/init.d/supervisor < supervisor.patch

sudo ln -s /opt/elixys/config/elixyssupervisord.conf  \ 
        /etc/supervisor/conf.d

sudo service crtmpserver restart
sudo service supervisor restart
