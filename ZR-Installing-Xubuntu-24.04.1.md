
## Installing on: zr-ThinkPad-T480:
2025-02-13

```bash
#----------------
# Download Xubuntu 24.04.1 from: https://xubuntu.org/download/

wget -P ~/Downloads "https://mirror.csclub.uwaterloo.ca/xubuntu-releases/24.04/release/xubuntu-24.04.1-desktop-amd64.iso"
wget -P ~/Downloads "https://mirror.csclub.uwaterloo.ca/xubuntu-releases/24.04/release/xubuntu-24.04.1-minimal-amd64.iso"
wget -P ~/Downloads "https://mirror.csclub.uwaterloo.ca/xubuntu-releases/24.04/release/SHA256SUMS"
wget -P ~/Downloads "https://mirror.csclub.uwaterloo.ca/xubuntu-releases/24.04/release/SHA256SUMS.gpg"

# Verify download:
cd ~/Downloads
cat SHA256SUMS | shasum -a 256 --check

#----------------
# Create bootable USB:
#   (see: https://www.cyberciti.biz/faq/creating-a-bootable-ubuntu-usb-stick-on-a-debian-linux/ )

# Plug in USB and find it's device name:
df

# Create bootable USB from image file:
sudo dd if=xubuntu-24.04.1-desktop-amd64.iso of=/dev/sdc bs=1M status=progress

# Warnings:
#   If grub gets installed on the USB installation device, simply reboot with the installation USB, 
#   log in, and run:
sudo dpkg-reconfigure grub-pc 
#   This will show a text interface where you can choose the installation disk(s).

```

```text
Boot target computer from USB:
    Insert USB
    Enter BIOS setup:
        Force shut down: Hold <Power> down for a few seconds.
        Power up, press <Enter> when prompted on the ThikPad startup screen.
    Press <F12> to select temporary boot media.
    Select: UCB HDD SanDisk Cruzer Edge
    Select: Try or Install Xubuntu
```

```bash
# Make sure you are using UEFI on the computer:
[ -d /sys/firmware/efi ] && echo "EFI boot" || echo "Legacy boot".

# Find HD size:
lsblk

sda 238.5 G
```

```text
Start Xubuntu installer from the shortcut on the desktop
Language: English
Keyboard layout: English (US)
Connect to Internet
    (*) Conect to a WiFi network
How would you like yo Install XubuntU?
    (*) Interactive Installation 
What apps would you like to install to start with? 
    (*) Xubuntu Desktop
Install recommended proprietary software?
    [x] Install third-party software for graphics and WiFi hardware 
    [x] Download and install support for additional media formats.
How do you want to install Xubuntu? 
    (*) Erase disk and install Xubuntu
        [Advanced features] 
            (*) Use LVM and encryption
Create a passphrase
    (ustal passphrase dla LUKS encryption)
Create your account
    Your name: ZR
    Your computer's name: zr-ThinkPad-T480
    Your username: zr
    Password: (ustal hasło)
    [x] Require my password to log in.
Select your tim zone 
    America/Toronto
Review your choices
    Partitions
        partition sda1 formatted as fat32 used for /boot/efi
        partition sda2 formatted as  ext4 used for /boot
        partition sda3 created
    [Install]

After successful installation, reboot from installation USB again and open Terminal.
```

```text
Shrink sda3 partition to make space for Veracrypt-encrypted data partition:    
  (based on: https://starbeamrainbowlabs.com/blog/article.php?article=posts%2F441-resize-luks-lvm.html )
```
```bash
sudo modprobe dm-crypt # Make sure that LUKS kernel is loaded.
sudo cryptsetup luksOpen /dev/sda3 crypt1 # Unlock the LUKS-encrypted drive.
# (enter passphrase)
sudo vgscan --mknodes # Make LVM to re-scan the available physical partitions.
sudo vgchange -ay # Activate logical volume.
sudo lsblk
```
```text
sda                          8:0    0 238.5G  0 disk  
├─sda1                       8:1    0     1G  0 part  
├─sda2                       8:2    0     2G  0 part  
└─sda3                       8:3    0 235.4G  0 part
  └─crypt1                 252:0    0 235.4G  0 crypt 
    └─ubuntu--vg-ubuntu-lv 252:1    0 235.4G  0 lvm

```
```bash
sudo lvdisplay # List available LVM partitions and their paths.
#   LV Path     /dev/ubuntu-vg/ubuntu-lv
#   LV Size     235.41 GiB
#
# After shrinking we want to leave max 118.4 GiB (127.13 GB) of unallocated space for the new partition.
# That is: after shrinking sda3 should be: 117 GiB 
#
sudo e2fsck -f -y -v -C 0 /dev/ubuntu-vg/ubuntu-lv # Check file system on LV and repair if necessary. 
sudo resize2fs -p /dev/ubuntu-vg/ubuntu-lv 117G # Shrink file system on LV.
sudo lvresize -L 117G /dev/ubuntu-vg/ubuntu-lv # Resize logical volume.
# Open: Menu > System > GParted
#   and resize /dev/sda3 to its now-minimum allowed size: 
#     Free space preceding (MiB): 0
#     New size (MiB):             119825
#     Free space following (MiB): 121249
#
# (Make sure to do: Edit > Apply All Operations )

sudo vgchange -an # Activate logical volume.
sudo cryptsetup luksClose crypt1 # Close the LUKS-encrypted drive.
```
```text
GParted
  Partition > New
    Free space preceding (MiB): 0
    New size (MiB):             121249
    Free space following (MiB): 0
    Align to: MiB
    Create as: Primary partition
    Partition name:
    File system: ext4
    Label:

  [+Add]
  [Apply]

Reboot the computer and remove installation media. 
You should be asked for the LUKS password at boot.
```

## Post-installation operations:

```bash
# Update and upgrade all obsolete packages after installation:
sudo apt update && sudo apt upgrade
```

```text
--------
Set single-click items opening:
    https://askubuntu.com/questions/880844/xubuntu-16-04-set-mouse-to-always-single-click

Single click to access items is done in two parts for Xfce. Your Desktop and File Manager are set separately.
For the Desktop: go to Applications > Settings > Desktop and in the Icons tab choose Single click to activate items.
For File Manager: Applications > System > Thunar File Manager , Edit > Preferences > Behavior > Navigation > Single click to activate items

--------
Configure desktop Panel:
  Add:
    - Action Buttons
    - Keyboard Layouts
    - System Load Monitor

--------
Add Polish keyboard:
  Settings > Keyboard > Layout > Add

--------
Add uBlock Origin to Firefox:
  https://ublockorigin.com/

--------
Configure Terminal:

Manually:
  Edit > Preferenes
    General:
      Cursor shape: Block, blinks
        Clipboard: 
          (check) Automatically copy selection to clipboard
          (uncheck) Show unsafe paste dialog
    Appearance:
      Font: 14pt
      Default geometry: 110/32
      
Set tap-click on the Touchpad:
  Settings > Mouse and Touchpad
    Devices > Touchpad > General: 
      [x] Tap Touchpad to click 
```

```bash
# Install VeraCrypt:
#   (based on: https://www.linuxcapable.com/install-veracrypt-on-ubuntu-linux/ )

sudo apt update && sudo apt upgrade
sudo add-apt-repository ppa:unit193/encryption -y # Import Veracrypt APT PPA
sudo apt update
sudo apt install veracrypt # Finalize Veracrypt installation.

# Add launcher to the desktop Panel:
#   Accessories > VeraCrypt > (Right-click) Add to Panel
#   Move it to the left in the Panel
```
```text
Create and mount a VeraCrypt volume in the dedicated partition:

/dev/sda4 --> /media/veracrypt1
    Use NTFS file system (not Ext4, even if this volume will only ever be mounted on Linux) 
    to avoid problems with filenames and file permissions while copying data to and from the external Veracrypt volume.
Add to Favourites in Veracrypt
```

```bash
# Copy 'dane' and user home directory from source system to the encrypted external storage:

# On source system: 

  # Close all editing sessions (VIM, LibreOffice, etc..)

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
rm -r ~/.vim/.swp
rm -r /media/veracrypt1/home/zr/.vim/.swp 

  # Copy home directory data to the internal encrypted storage:
rsync -avW --delete ~ /media/veracrypt1/home

  # Copy the internal encrypted storage to external:
rsync -avW --delete /media/veracrypt1/ /media/veracrypt2/ 

# Copy 'dane' and user home directory from the encrypted external storage to the target system:

# On target system: 

  # Copy the external encrypted storage to internal:
rsync -avW --delete /media/veracrypt2/ /media/veracrypt1/ 
```

```bash
# Install VIM:
sudo apt install vim

# Configure and test VIM:
cd ~
cp -R /media/veracrypt1/home/zr/.vimrc .
cp /media/veracrypt1/home/zr/.viminfo .
```
```txt
Useful Vim commands:
\ww
:syntax sync fromstart
:set nonumber | set norelativenumber
:!./datedlines.py | sort | grep ^2024-02- | grep MasterCard
:!find md -type f | xargs -d '\n' | grep -i usss
```

```bash
# Migrate bash shell configuration:
cp ~/.bashrc ~/.bashrc-ORG
cp /media/veracrypt1/home/zr/.bashrc ~/.bashrc
cp ~/.bash_aliases ~/.bash_aliases-ORG
cp /media/veracrypt1/home/zr/.bash_aliases ~/.bash_aliases
  # Edit aliases file and delete what is already obsolete:
vim ~/.bash_aliases

# Configure and test Mail Reader (Thunderbird):
cd ~
cp -R /media/veracrypt1/home/zr/.thunderbird .
rm -R .thunderbird/Crash\ Reports/

vim ~/.thunderbird/installs.ini
# Set:
Default=/media/veracrypt1/thunderbird.zrprofile

# Install and configure Git:
sudo apt install git
git config --global user.email "zbig@rogowski.ca"
git config --global user.name "Zbigniew Rogowski"
git log --pretty=format"%C(auto)%h %ci %x09%Cgreen%s" -20

# Install Python
# ( It may be already installed, check: which python3 )
sudo apt install python3

# Copy Desktop items:
cp -R /media/veracrypt1/home/zr/Desktop/* ~/Desktop
# Test migrated desktopm shortcuts.

# Arrange and review Desktop items:
#   Do not store personal documents in ~/Desktop,
#   instead, always use symbolic links to documents stored on: /media/veracrypt1/

# Associate PDF documents with "Atril Document Viewer"

# Install xsltproc:
sudo apt install xsltproc

# Install pandoc:
sudo apt install pandoc

# Install curl:
type -p curl >/dev/null || (sudo apt update && sudo apt install curl -y)

# Install CLI GitHub client 'gh':
#   https://cli.github.com/
#     https://github.com/cli/cli/blob/trunk/docs/install_linux.md

(type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y)) \
	&& sudo mkdir -p -m 755 /etc/apt/keyrings \
        && out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        && cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
	&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
	&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
	&& sudo apt update \
	&& sudo apt install gh -y

# Upgrade CLI GitHub client 'gh':
sudo apt update 
sudo apt install gh

# Publish this page to rogowskz.github.io
# DONE.
```

```bash
# Test budget update:
ctl
bu

# Test finmodel:
cfm
bu

# Test dane_out
dane_out

# Test Timeline site generation:
ctl
rm -r html
python3 build/build.py . .
xdg-open html/index.html
```

## TODOs:

```bash
# Test GPG
# TODO:

# Test printing:
# TODO:

# Test scanning:
# TODO:

# Enable hibernation:
# TODO: ??

# Install GnuCash
# TODO: ??
```

```text
Log in to Gmail accounts:
  + rogowskz@gmail.com
  - zbigpro@gmail.com
  - renata.rogowska@gmail.com
```

## Cleanup

```bash
# Remove no longer needed installed packages:
sudo apt autoremove
sudo apt autoclean
```

## Legacy

--------------------------------------------
[ZR Installing Xubuntu 22.04](ZR-Installing-Xubuntu-22.04)

    Install Brother printer drivers.

    Download from http://support.brother.com/g/b/productsearch.aspx?c=us&lang=en&content=dl
        gunzip linux-brprinter-installer-2.*.gz
        sudo bash linux-brprinter-installer-2.*
        Enter machine name
        When you see the message “Will you specify the DeviceURI ?” USB Users: Choose N(No). Network Users: Choose Y(Yes).
        If scanner isn’t working
            brsaneconfig4 -a name=Scanner model='modelname' ip='ip-address'
        Check network mapping with
            nmap 'IP range'/24

