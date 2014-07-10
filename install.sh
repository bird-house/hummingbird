#!/bin/bash
PWD=`pwd`
BUILDOUT_DIR=`dirname $0`
DOWNLOAD_CACHE=downloads
ANACONDA_HOME="$HOME/anaconda"
ANACONDA_FILE=Miniconda-latest-Linux-x86_64.sh
ANACONDA_URL=http://repo.continuum.io/miniconda/$ANACONDA_FILE
#ANACONDA_MD5=01b39f6b143102e6e0008a12533c1fc9


# actions before build
function pre_build() {
    clean_build
    upgrade
    setup_cfg
    setup_os
    install_java
    install_anaconda
    #install_conda
}

function clean_build() {
    echo "Cleaning buildout ..."
    rm -rf $BUILDOUT_DIR/downloads
    rm -rf $BUILDOUT_DIR/eggs
    rm -rf $BUILDOUT_DIR/develop-eggs
    rm -rf $BUILDOUT_DIR/parts
    rm -rf $BUILDOUT_DIR/bin
    rm -f $BUILDOUT_DIR/.installed.cfg
    rm -rf $BUILDOUT_DIR/*.egg-info
    echo "Cleaning buildout ... Done"
}

# upgrade stuff which can not be done by buildout
function upgrade() {
    if [ -f /etc/debian_version ] ; then
        echo "Upgrade on Debian/Ubuntu"
        sudo apt-get -y --force-yes purge supervisor
        sudo apt-get -y --force-yes purge nginx-full
        sudo apt-get -y --force-yes purge mongodb mongodb-server mongodb-clients mongodb-dev
        sudo apt-get -y --force-yes purge tomcat7
        sudo apt-get -y --force-yes purge gunicorn

        sudo apt-get -y --force-yes autoremove
    elif [ -f /etc/redhat-release ] ; then
        echo "Upgrade on Redhat/CentOS"
        sudo yum -y erase mongodb mongodb-server
    fi
}

# set configurion file for buildout
function setup_cfg() {
    if [ ! -d $DOWNLOAD_CACHE ]; then
        echo "Creating buildout downloads cache $DOWNLOAD_CACHE."
        mkdir -p $DOWNLOAD_CACHE
    fi

    if [ ! -f custom.cfg ]; then
        echo "Copy default configuration to $BUILDOUT_DIR/custom.cfg"
        cp "$BUILDOUT_DIR/custom.cfg.example" "$BUILDOUT_DIR/custom.cfg"
    else
        echo "Using custom configuration $BUILDOUT_DIR/custom.cfg"
    fi
}

# install os packages needed for bootstrap
function setup_os() {
    if [ -f /etc/debian_version ] ; then
        sudo apt-get -y --force-yes install build-essential wget myproxy
    elif [ -f /etc/redhat-release ] ; then
        sudo rpm -i http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
        sudo yum install -y gcc-c++ wget myproxy
    fi
}

function install_java() {
    if [ -f /etc/debian_version ] ; then
        sudo apt-get install -y --force-yes openjdk-7-jre openjdk-7-jdk
        if [ -d /usr/lib/jvm/java-7-openjdk-amd64 ] ; then
            sudo update-alternatives --set java /usr/lib/jvm/java-7-openjdk-amd64/jre/bin/java
        elif [ -d /usr/lib/jvm/java-7-openjdk-i386 ] ; then
            sudo update-alternatives --set java /usr/lib/jvm/java-7-openjdk-i386/jre/bin/java
       fi
    fi  
    if [ -f /etc/redhat-release ] ; then
        sudo yum install -y java-1.7.0-openjdk java-1.7.0-openjdk-devel 
    fi 
}

function install_anaconda() {
    # download miniconda setup script to download cache with wget
    wget -q -c -O $DOWNLOAD_CACHE/$ANACONDA_FILE $ANACONDA_URL

    # md5 check sum on the current file you downloaded and save results to 'test1'
    test_md5=`md5sum "$DOWNLOAD_CACHE/$ANACONDA_FILE" | awk '{print $1}'`;
    #if [ "$test_md5" != $ANACONDA_MD5 ]; then 
    #    echo "checksum didn't match!"
    #    #echo "Installing Anaconda ... Failed"
    #    #exit 1
    #fi

    # run miniconda setup, install in ANACONDA_HOME
    if [ ! -d $ANACONDA_HOME ]; then
        sudo bash "$DOWNLOAD_CACHE/$ANACONDA_FILE" -b -p $ANACONDA_HOME
         # add anaconda path to user .bashrc
        #echo -e "\n# Anaconda PATH added by climdaps installer" >> $HOME/.bashrc
        #echo "export PATH=$ANACONDA_HOME/bin:\$PATH" >> $HOME/.bashrc
    fi

    # add anaconda to system path for all users
    #echo "export PATH=$ANACONDA_HOME/bin:\$PATH" | sudo tee /etc/profile.d/anaconda.sh > /dev/null
    # source the anaconda settings
    #. /etc/profile.d/anaconda.sh

    sudo chown -R $USER $ANACONDA_HOME

    echo "Installing Anaconda ... Done"
}

function install_conda() {
    $ANACONDA_HOME/bin/conda install --yes -c https://conda.binstar.org/pingucarsti python mako
}

# run install
function install() {
    echo "Installing ClimDaPS ..."
    echo "BUILDOUT_DIR=$BUILDOUT_DIR"
    echo "DOWNLOAD_CACHE=$DOWNLOAD_CACHE"

    cd $BUILDOUT_DIR
    
    pre_build
    $ANACONDA_HOME/bin/python bootstrap.py -c custom.cfg
    echo "Bootstrap ... Done"
    bin/buildout -c custom.cfg

    cd $PWD

    echo "Installing ClimDaPS ... Done"
}

function usage() {
    echo "Usage: $0"
    exit 1
}

install
