#!/bin/bash

if [ -f /etc/debian_version ] ; then
    echo "Installing Debian/Ubuntu packages ..."
    # fix for cdo/netcdf4 on debian
    # sudo apt-get -y install libjpeg8
elif [ -f /etc/redhat-release ] ; then
    echo "Installing RedHat/CentOS packages ..."
    #sudo yum -y install wget
elif [ `uname -s` = "Darwin" ] ; then
    echo "Installing MacOSX/Homebrew packages ..."
    #brew tap homebrew/science
    #brew install cdo
fi
