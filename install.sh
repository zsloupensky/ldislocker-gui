#! /bin/sh
gcc ldislocker-gui.c -o /tmp/ldislocker-gui
addgroup dislock

cp ldislocker-gui.py /usr/local/bin/
cp /tmp/ldislocker-gui /usr/local/bin/

chown root:dislock /usr/local/bin/ldislocker-gui.py 
chmod 750 /usr/local/bin/ldislocker-gui.py

chown root:dislock /usr/local/bin/ldislocker-gui 
chmod 4750 /usr/local/bin/ldislocker-gui

echo "add your account into group dislock"
pip install python-tk
