# Ldislocker GUI

GUI for dislocker tool - bitlocker for Linux

Project is based on https://github.com/soachishti/dislocker-gui

Thanks for inspiration :-)

install/ using:

Firstly install dislocker tools and python-tk: 

apt install dislocker python-tk

or 

yum install dislocker python-tk


## run script ldislocker-gui as root:

sudo ldislocker-gui.py $USER

Script can use one parameter - username. The mounted disk rights will be set for the user.

## or install:

git clone https://github.com/zsloupensky/ldislocker-gui.git

cd ldislocker-gui

sudo sh install.sh


Add your account into group dislock and relogon.

Then you can run ldislock-gui or /usr/share/ldislocker-gui if /usr/share/bin is not in PATH env. 



