

--------------------------------------------------------------------------------------
# Installing on: zr-ThinkPad-T480:
2025-02-06

- Downloaded Xubuntu 24.04.1 Minimal image file [Xubuntu Download](https://xubuntu.org/download/)
    - `wget -P ~/Downloads "https://mirror.csclub.uwaterloo.ca/xubuntu-releases/24.04/release/xubuntu-24.04.1-desktop-amd64.iso"`
    - `wget -P ~/Downloads "https://mirror.csclub.uwaterloo.ca/xubuntu-releases/24.04/release/xubuntu-24.04.1-minimal-amd64.iso"`
    - `wget -P ~/Downloads "https://mirror.csclub.uwaterloo.ca/xubuntu-releases/24.04/release/SHA256SUMS"`
    - `wget -P ~/Downloads "https://mirror.csclub.uwaterloo.ca/xubuntu-releases/24.04/release/SHA256SUMS.gpg"`

- Created bootable USB [https://www.cyberciti.biz/faq/creating-a-bootable-ubuntu-usb-stick-on-a-debian-linux/](https://www.cyberciti.biz/faq/creating-a-bootable-ubuntu-usb-stick-on-a-debian-linux/)
```bash
# Verify download:
cd ~/Downloads
cat SHA256SUMS | shasum -a 256 --check

# Plug in USB and find it's device name:
df

# Create bootable USB from image file:
sudo dd if=xubuntu-24.04.1-desktop-amd64.iso of=/dev/sdc bs=1M status=progress
```
- Booted from USB:

To enter BIOS setup:
    - Force shut down: Hold <Power> down for a few seconds.
    - Power up, press <Enter> when prompted on the ThikPad startup screen.

 To start from USB: 
    - Insert USB
    - Enter BIOS setup and select <F12> to select temporary boot media.

# Find HD size:
```bash
lsblk
```
sda 238.5 G

[Brett Klamer: The Complete Installation Guide for Xubuntu 22.04 (local copy)](Brett-Klamer-The-Complete-Installation-Guide-for-Xubuntu-22.04-local-copy.md)

- Reboot from bootable USB with Xubuntu 24.04.1 LTS
- Use: "Try or Install XUbuntu"
- Make sure you are using UEFI on the computer:
```bash
[ -d /sys/firmware/efi ] && echo "EFI boot" || echo "Legacy boot".
```
* Follow directions from https://help.ubuntu.com/community/Full_Disk_Encryption_Howto_2019 :
```bash

# Identify installation device:
























--------------------------------------------------------------------------------------
# Installing on: zr-ThinkPad-T450s:
2024-03-10

To enter BIOS setup:
    - Force shut down: Hold <Power> down for a few seconds.
    - Power up, press <Enter> when prompted on the ThikPad startup screen.

 To start from USB: 
    - Insert USB
    - Enter BIOS setup and select <F12> to select temporary boot media.

# Find HD size:
```bash
lsblk
```
sda 238.5 G

# [Brett Klamer: The Complete Installation Guide for Xubuntu 22.04](https://brettklamer.com/diversions/non-statistical/the-complete-installation-guide-for-xubuntu-22.04/)

* Reboot from bootable USB with Xubuntu 22.04
* Use: "Try or Install XUbuntu"
* Make sure you are using UEFI on the computer:
```bash
[ -d /sys/firmware/efi ] && echo "EFI boot" || echo "Legacy boot".
```
* Follow directions from https://help.ubuntu.com/community/Full_Disk_Encryption_Howto_2019 :
```bash

# Identify installation device:
sudo -i # switch to root user
lsblk # determine the target drive
export DEV="/dev/sda" # save reference to drive location
export DM="${DEV##*/}" # save reference to encrypted device mapper (without leading /dev/)
export DEVP="${DEV}" # save reference to base partition name

# Partitioning:
sgdisk --print $DEV # check for pre-existing partitions
sgdisk --zap-all $DEV # delete all previous partitions 

sgdisk --new=1:0:+768M $DEV # /boot/ , 768.0 MiB
sgdisk --new=2:0:+2M $DEV   # bios_boot, for BIOS-mode GRUB's core image , 2.0 MiB
sgdisk --new=3:0:+128M $DEV # EFI system partition , 128.0 MiB
sgdisk --new=5:0:+119G $DEV # space for the operating system and installed programs , 119.0 GiB
sgdisk --new=6:0:0 $DEV # remaining space 118.6 GiB (127.35 GB) for veracrypt-encypted  private data partition.

sgdisk --typecode=1:8301 --typecode=2:ef02 --typecode=3:ef00 --typecode=5:8301 --typecode=6:8301 $DEV
sgdisk --change-name=1:/boot --change-name=2:GRUB --change-name=3:EFI-SP --change-name=5:rootfs --change-name=6:dane $DEV
sgdisk --hybrid 1:2:3 $DEV

sgdisk --print $DEV # after rebooting, to check all new partitions

# LUKS encrypt:
cryptsetup luksFormat --type=luks1 ${DEVP}1 # for the /boot/ partition
alamakota

cryptsetup luksFormat ${DEVP}5 # for the OS partition
alamakota

# LUKS unlock:
cryptsetup open ${DEVP}1 LUKS_BOOT
cryptsetup open ${DEVP}5 ${DM}5_crypt

ls /dev/mapper
# expected response: 
# control LUKS_BOOT sda5_crypt

# Format filesystems:
mkfs.ext4 -L boot /dev/mapper/LUKS_BOOT
mkfs.vfat -F 16 -n EFI-SP ${DEVP}3

# LVM Logical Volume Manager:
# Naming scheme for VG (LVM Volume Group) and LV (Logical Volume) in different releases of ubuntu
flavour="$( sed -n 's/.*cdrom:\[\([^ ]*\).*/\1/p' /etc/apt/sources.list )"
release="$( lsb_release -sr | tr -d . )"
if [ ${release} -ge 2204 ]; then VGNAME="vg${flavour,,}"; else VGNAME="${flavour}--vg"; fi 
export VGNAME
# Create volumes:
pvcreate /dev/mapper/${DM}5_crypt
vgcreate "${VGNAME}" /dev/mapper/${DM}5_crypt
lvcreate -L 8G -n swap_1 "${VGNAME}" # SWAP partition
lvcreate -L 8G -n home "${VGNAME}" # HOME partition
lvcreate -l 80%FREE -n root "${VGNAME}"
```

* Start Xubuntu installer from the shortcut on the desktop
* Language: English
* Keyboard layout: English (US)
* Normal Installation, Download updates while installing..., Install third-party software for...
* Installation type: Something else
* Edit partitions, assign mount points / /boot /home swap
* Where are you? Toronto
* Who are you:
    * Your name: ZR
    * Your computer name: zr-ThinkPad-T450s
    * Pick a username: zr
    * Choose a password: <set user password>
    * "Require my password to log in"
    * [Continue]
* IMMEDIATELY ENABLE ENCRYPTED GRUB!
```bash
while [ ! -d /target/etc/default/grub.d ]; do sleep 1; done; echo "GRUB_ENABLE_CRYPTODISK=y" > /target/etc/default/grub.d/local.cfg
cat /target/etc/default/grub.d/local.cfg # check if text added
```

* After successful installation, choose [Continue Testing].

```bash
# Create a change-root environment to work in the newly installed OS:
mount /dev/mapper/${VGNAME}-root /target
for n in proc sys dev etc/resolv.conf; do mount --rbind /$n /target/$n; done
chroot /target
mount -a

# Configure cryptsetup-initramfs and key file
apt install -y cryptsetup-initramfs
echo "KEYFILE_PATTERN=/etc/luks/*.keyfile" >> /etc/cryptsetup-initramfs/conf-hook
echo "UMASK=0077" >> /etc/initramfs-tools/initramfs.conf

# Create a randomised key-file of 4096 bits (512 bytes), secure it, and add it to the LUKS volumes
mkdir /etc/luks
dd if=/dev/urandom of=/etc/luks/boot_os.keyfile bs=512 count=1

chmod u=rx,go-rwx /etc/luks
chmod u=r,go-rwx /etc/luks/boot_os.keyfile

cryptsetup luksAddKey ${DEVP}1 /etc/luks/boot_os.keyfile
cryptsetup luksAddKey ${DEVP}5 /etc/luks/boot_os.keyfile

# Add the keys to the crypttab
echo "LUKS_BOOT UUID=$(blkid -s UUID -o value ${DEVP}1) /etc/luks/boot_os.keyfile luks,discard" >> /etc/crypttab
echo "${DM}5_crypt UUID=$(blkid -s UUID -o value ${DEVP}5) /etc/luks/boot_os.keyfile luks,discard" >> /etc/crypttab

# Update the initramfs files to add the cryptsetup unlocking scripts and the key-file
update-initramfs -u -k all

```

# Post-installation operations:

## Set single-click items opening:

https://askubuntu.com/questions/880844/xubuntu-16-04-set-mouse-to-always-single-click

Single click to access items is done in two parts for Xfce. Your Desktop and File Manager are set separately.
For the Desktop: go to Applications > Settings > Desktop and in the Icons tab choose Single click to activate items.
For File Manager: Applications > System > Thunar File Manager , Edit > Preferences > Behavior > Navigation > Single click to activate items

## Configure desktop Panel:
- Add:
    - Action Buttons
    - Keyboard Layouts
    - System Load Monitor

## Add Polish keyboard:

- Settings > Keyboard > Layout > Add

## Configure Terminal:

- Manually:
    - Edit > Preferenes
        - General:
            - Cursor shape: Block, blinks
            - Clipboard: 
                - (check) Automatically copy selection to clipboard
                - (uncheck) Show unsafe paste dialog
        - Appearance:
            - Font: 14pt
            - Default geometry: 160/40
            - To set default position: 
                - vim ~/.config/xfce4/terminal/terminalrc
                - `MiscDefaultGeometry=160x40+270+120`

- To copy from the previous system:
    - `cp /media/veracrypt1/home/rogowskz/.config/xfce4/terminal/terminalrc ~/.config/xfce4/terminal/terminalrc`

## Install Vim:

```bash
sudo apt install vim
```

## Install VeraCrypt:

[How to Install VeraCrypt on Ubuntu 22.04 or 20.04](https://www.linuxcapable.com/install-veracrypt-on-ubuntu-linux/)

```bash
sudo apt update
sudo apt upgrade
sudo add-apt-repository ppa:unit193/encryption -y
sudo apt update
sudo apt install veracrypt
```
- Add launcher to the desktop Panel:
    - Accessories > VeraCrypt > (Right-click) Add to Panel
    - Move it to the left in the Panel

## Create and mount a VeraCrypt volume in the dedicated partition:

- /dev/sda6 --> /media/veracrypt1
    - Use NTFS file system (not Ext4, even if this volume will only ever be mounted on Linux) 
      to avoid problems with filenames and file permissions while copying data to and from the external Veracrypt volume.
- Add to Favourites in Veracrypt

## Copy 'dane' and user home directory from source system to the encrypted external storage:

```bash
# On source system: 

  # Clenup unnecessary data:
    # See how much data is there:
du -sh ~
    # Decide on what to delete before copying, and do it:
      # Not-hidden files/dirs:
ls -1 ~ 
rm ~/Downloads/*
      # Hidden files/dirs:
ls -a1 ~ | grep "^\."
rm -r ~/.cache/*

  # Edit aliases file and delete what is already obsolete:
vim ~/.bash_aliases

  # Copy home directory data to the internal encrypted storage:
rsync -avW --delete ~ /media/veracrypt1/home

  # Copy the internal encrypted storage to external:
rsync -avW --delete /media/veracrypt1/ /media/veracrypt2/ 
```

## Copy 'dane' and user home directory from the encrypted external storage to the target system:

```bash
# On target system: 

  # Copy the external encrypted storage to internal:
rsync -avW --delete /media/veracrypt2/ /media/veracrypt1/ 

  # Copy ~/Desktop from the source system to the target:
cp -R /media/veracrypt1/home/rogowskz/Desktop/* ~/Desktop
```

## Merge home dir data from the source system to the target:

```bash
# Copy Shell configuration:
cp ~/.bash_aliases ~/.bash_aliases-BAK
cp /media/veracrypt1/home/rogowskz/.bash_aliases ~

#-- cp ~/.bash_logout ~/.bash_logout-BAK
#-- cp /media/veracrypt1/home/rogowskz/.bash_logout ~

cp ~/.bashrc ~/.bashrc-BAK
cp /media/veracrypt1/home/rogowskz/.bashrc ~

# Copy Vim configuration:
cp /media/veracrypt1/home/rogowskz/.vimrc ~
cp -R /media/veracrypt1/home/rogowskz/.vim ~
rm -r ~/.vim/.swp/*

```

## Configure Vim:

Useful Vim commands:

```txt
\ww

:syntax sync fromstart

:!./datedlines.py | sort | grep ^2024-02- | grep MasterCard

:!find md -type f | xargs -d '\n' | grep -i usss

```

## Configure Thunderbird mail client:

```bash
vim ~/.thunderbird/installs.ini
# Set:
Default=/media/veracrypt1/thunderbird.zrprofile

cp ~/.thunderbird/profiles.ini ~/.thunderbird/profiles.ini-BAK 
vim ~/.thunderbird/profiles.ini /media/veracrypt1/home/rogowskz/.thunderbird/profiles.ini
# manually merge profiles data.

```

## Install curl:

```bash
type -p curl >/dev/null || (sudo apt update && sudo apt install curl -y)
```

## Install pandoc:
```bash
sudo apt-get install pandoc
```

## Install xsltproc:
```bash
sudo apt-get update -y
sudo apt-get install -y xsltproc
```

## Log in to Gmail accounts:
+ rogowskz@gmail.com
+ zbigpro@gmail.com
+ renata.rogowska@gmail.com

## Install GitHub CLI:
https://cli.github.com/
    https://github.com/cli/cli/blob/trunk/docs/install_linux.md

```bash
type -p curl >/dev/null || (sudo apt update && sudo apt install curl -y)

curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
&& sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | \
sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \
&& sudo apt install gh -y
```

## Install VLC Media Player:
```bash
sudo apt install vlc -y
```

#############################################

## Fix playing .mp4 videos with Parole Media Player:
TODO:
https://www.google.com/search?channel=fs&client=ubuntu-sn&q=parole+media+player+mp4+not+showing
https://forum.xfce.org/viewtopic.php?id=10786
https://blog.programster.org/xfce-slow-desktop-compositing
https://forums.gentoo.org/viewtopic-t-922192-start-0.html
https://learningnotebook.tech.blog/2019/08/16/how-do-i-reset-all-my-xfce-desktop-settings/


## Install Brother printer drivers:
## Conect Brother printer - wireless:
TODO: 

## Enable hibernation:
TODO: 

## Configure GPG:
TODO: 

## Install ~/gdrive CLI utility:
TODO: 

## Clone ZR-HP-desktop - except /dev/sda6 partition:
TODO: 


#############################################

https://brettklamer.com/diversions/non-statistical/the-complete-installation-guide-for-xubuntu-22.04/#post-install

## (?) Enable Firewall
## (?) Edit the Hosts file
## (?) TRIM for SSDs
## (?) Randomize MAC address

#############################################

## (?) Install [GnuCash](https://www.gnucash.org/)

#############################################
#############################################

--------------------------------------------------------------------------------------
# Installing on: ZR-HP-desktop

Zrobione.

--------------------------------------------------------------------------------------
# Installing on: ZR-HP-8560p (HP EliteBook 8560p)

# Find HD size:
```bash
lsblk
```
sda 298.1 G

# Find Xubuntu installed version:
```bash
lsb_release -a
```

Power + Esc - to enter setup
    F1  - system information
        Processor Type: Intel Core i7-2620M CPU 
        Processor Speed: 2.70 GHz
        Memory Size: 8192 MB RAM
Power + F9  - to enter boot device options
Power + F10 - to enter BIOS setup

!! UEFI not fully supported!

ZR decision: Abandon installation. Keep this system as a spare one, on the previous version of Xubuntu (20.04.4 LTS)

--------------------------------------------------------------------------------------
Poprzednia instalacja:  [XUbuntuInstallation](../XUbuntuInstallation)

  
