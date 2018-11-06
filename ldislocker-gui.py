#! /usr/bin/python
import psutil
from subprocess import call, Popen, PIPE
import os
import sys
import logging
import pwd
import re
from time import sleep

from Tkinter import Tk,Button,Toplevel,Label,Entry,END,Listbox,SINGLE
        
logging.basicConfig(level=logging.DEBUG)

MSG_PERMISSION_DENIED   = "Permission denied"
MSG_VOLUME_HEADER       = "Cannot parse volume header"
MSG_INVALID_DECRYPT         = "None of the provided decryption mean is decrypting the keys"

class DislockerGUI():
    bitlocker_path = "/media/bitlocker"
    listOfDevices=[]
    user=''

    def __init__(self,user='root'):
        # sudo permission check
        if os.getuid() != 0:
            raise Exception("Permission required, run with sudo.")
        user=user.lower()
        if not re.search('^[abcdefghijklmnopqrstuvwxyz_]([abcdefghijklmnopqrstuvwxyz0-9_-]{0,31}|[abcdefghijklmnopqrstuvwxyz0-9_-]{0,30}\\$)$', user):
            raise Exception("username is not valid")
        print('user: '+user)
        self.user=user

    def is_bitlocker_disk(self, disk):
        cmd = "dislocker -r -V {}".format(disk)

        p = Popen(cmd.split(" "), stdout=PIPE)
        stdout = p.stdout.read()

        print (disk)
        print (stdout)
        print ("="*80)

        if MSG_VOLUME_HEADER in stdout:
            return False
        elif MSG_INVALID_DECRYPT in stdout:
            return True
        else:
            raise Exception(stdout)
    def __get_disks(self):
        devices=[]
        cmd='dislocker-find'
        p=Popen(cmd, stdout=PIPE, shell=True)
        stdout=p.stdout.read()
        [devices.append(dev) for dev in stdout.split('\n') if dev !='']
        return devices
    def __get_disks_old(self):
        # https://github.com/MrVallentin/mount.py/blob/master/mount.py
        # Return USB or External Drive's Partitions
        with open("/proc/partitions", "r") as f:
            devices = []
            
            for line in f.readlines()[2:]: # skip header lines
                words = [ word.strip() for word in line.split() ]
                minor_number = int(words[1])
                device_name = words[3]
                
                if (minor_number % 16) == 0:
                    path = "/sys/class/block/" + device_name
                    
                    if os.path.islink(path):
                        if os.path.realpath(path).find("/usb") > 0:
                            device = "/dev/" + device_name
                            cmd = "fdisk -l {}".format(device)
                            p = Popen(cmd, stdout=PIPE, shell=True)
                            stdout = p.stdout.read()
                            partitions = stdout.split("\n")[-2].split()[0].strip()
                            
                            devices.append(partitions)
            
            return devices

    def __get_mount_path(self, device):
        name = os.path.basename(device)
        path = "/media/" + name
        return path

    def __is_mounted(self, device):
        return os.path.ismount(self.__get_mount_path(device))

    def __get_size(self, device):
        path = "/sys/block/" + os.path.basename(device)[:3] + "/size"
        print (path)
        if os.path.exists(path):
            with open(path, "r") as f:
                size = int(f.read().strip()) * 512
                size = str(size / 1024 ** 3)
                return "({} GB)".format(size)

        return "()"

    def get_unmounted_disks(self):
        disks = []
        media_device = self.__get_disks()
        logging.debug("Media Device Found: " + str(media_device))
        for device in media_device:
            if self.__is_mounted(device) == False:
                disks.append(device)
        logging.debug("Unmounted Device: " + str(disks))
        return disks

    def mount(self, device, password):
        mount_path = self.__get_mount_path(device)
        bitlocker_path2=self.bitlocker_path+'-'+os.path.basename(device)
        os.system("mkdir -p " + mount_path)
        os.system("mkdir -p " + bitlocker_path2)
        os.system('chown {} '.format(self.user) + bitlocker_path2)
        os.system('chown {} '.format(self.user) + mount_path)
        uid=0
        if self.user != '':
            uid=pwd.getpwnam(self.user)[2]
        cmd = "dislocker -V {} -u{} -- -o uid={},gid=0,rw {} ; ".format(device, password,uid,bitlocker_path2)
        cmd += "mount -o loop,uid={},gid=0,rw {}/dislocker-file {}".format(uid,bitlocker_path2, mount_path)

        logging.debug("Mounting device to " + mount_path)
        #logging.debug("Executing command: " + cmd)

        p = Popen(cmd, stdout=PIPE, shell=True)
        stdout = p.stdout.read()
        logging.debug(stdout)
        os.system('chown {} '.format(self.user) + mount_path)
        os.system('chown {} '.format(self.user) + bitlocker_path2)

        #while self.__is_mounted(mount_path):
        #    logging.debug("Waiting for " + mount_path + " to mount")
        #    sleep(1)
            
    def unmount(self, device):
        mount_path = self.__get_mount_path(device)
        bitlocker_path2=self.bitlocker_path+'-'+os.path.basename(device)
        cmd = "umount {}".format(mount_path) +'; '
        cmd += "umount {}".format(bitlocker_path2)
        logging.debug("Executing command: " + cmd)
        p = Popen(cmd, stdout=PIPE, shell=True)
        stdout = p.stdout.read()
        logging.debug(stdout)

    class PasswordDialog:
        def __init__(self,parent,device):
            self.password=''
            proot = self.proot = Toplevel(parent)
            proot.title("Password")
            Label(proot, text = 'Password for' + device).pack(side = 'top')
            self.pwdbox = Entry(proot, show = '*')
            self.pwdbox.pack(side = 'top')
            self.pwdbox.focus()
            self.pwdbox.bind('<Return>', self.onpwdentry)
            Button(proot, command=self.onokclick, text = 'Submit').pack(side = 'top')
        def onpwdentry(self,evt):

            self.password = self.pwdbox.get()
            self.proot.destroy()
        def onokclick(self):
            self.password = self.pwdbox.get()
            self.proot.destroy()
            
            

    def mountDialog(self):
        self.password = ''
        self.device=''
        self.listOfDevices=[]

        def refreshDevicesList():
            self.listOfDevices=[]
            bitLockDevices=self.__get_disks()
            logging.debug('bitlock devices: {}'.format(bitLockDevices))
            unmountedDisks=self.get_unmounted_disks()
            logging.debug('unmounted devices: {}'.format(unmountedDisks))
            for d in bitLockDevices:
                isMounted=False
                if d not in unmountedDisks:
                    isMounted=True
                self.listOfDevices.append({'name':d,'mounted':isMounted,})

        def refreshClick():
            refreshDevicesList()
            deviceList.delete(0,END)
            for d in self.listOfDevices:
                dd=d['name']
                if d['mounted']:
                    dd+=' (mounted)'
                deviceList.insert(END,dd)

        def mountClick():
            #password = pwdbox.get()
            device = self.listOfDevices[deviceList.curselection()[0]]['name']
            passwd=self.PasswordDialog(root,device)
            root.wait_window(passwd.proot)
            password=passwd.password
            #password = self.passwordDialog(device)
            logging.debug('selected device:' + device)
            self.mount(device, password)
            refreshClick()

        def umountClick():
            device = self.listOfDevices[deviceList.curselection()[0]]['name'] 
            logging.debug('selected device:' + device)
            self.unmount(device)
            refreshClick()

        root = Tk()
        root.title("Dislocker GUI")
        #pwdbox = Entry(root, show = '*')
        Button(root, command=refreshClick, text = 'refresh').pack(side = 'top')
        deviceList = Listbox(root,selectmode=SINGLE)
        deviceList.pack()
        refreshClick()
        #for d in self.get_unmounted_disks():
        #     deviceList.insert(END,d)

        #device_info = 'Device: ' + device + self.__get_size(device)

        #Label(root, text = device_info).pack(side = 'top')

        #Label(root, text = 'Password').pack(side = 'top')

        #pwdbox.pack(side = 'top')
        #pwdbox.bind('<Return>', onpwdentry)
        #Button(root, command=onokclick, text = 'Submit').pack(side = 'top')
        Button(root, command=mountClick, text = 'mount').pack(side = 'top')
        Button(root, command=umountClick, text = 'umount').pack(side = 'top')

        root.mainloop()
        #return self.password
        logging.debug('selected device: '+ self.device)
        return {'password':self.password,'device': self.device}

    def run(self):
        self.mountDialog()
        #while True:    
        #    devices = d.get_unmounted_disks()
        #    if len(devices) != 0:
        #        #device = devices[0]
        #        pasdev = self.passwordDialog(devices)
        #        password=pasdev['password']
        #        device=pasdev['device']
        #        d.mount(device, password)
        #        sleep(3000)

u=''
if len(sys.argv)>1:
    u=str(sys.argv[1])
d = DislockerGUI(user=u)
d.run()
