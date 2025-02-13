
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

# Install Vim:
sudo apt install vim
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

# Copy 'dane' and user home directory from the encrypted external storage to the target system:

# On target system: 

  # Copy the external encrypted storage to internal:
rsync -avW --delete /media/veracrypt2/ /media/veracrypt1/ 

```






--------------------------------------------
[ZR Installing Xubuntu 22.04](ZR-Installing-Xubuntu-22.04)

Post install options

#----------------------------------------------------------------------
# Update apt
#----------------------------------------------------------------------
sudo apt update
sudo apt full-upgrade

#----------------------------------------------------------------------
# Remove unwanted software
#----------------------------------------------------------------------
sudo apt purge '^brltty.*' '^espeak.*' '^hplip.*' '^libhpmud0.*' '^libsane-hpaio.*' '^parole.*' '^printer-driver.*' '^speech-dispatcher.*' '^whoopsie.*' '^libwhoopsie0.*' '^popularity-contest.*' '^pidgin.*'

# Cleanup
sudo apt autoremove
sudo apt autoclean

#----------------------------------------------------------------------
# Install software
#----------------------------------------------------------------------
# General
sudo apt install git libssl-dev curl build-essential checkinstall autoconf automake libdbd-sqlite3 software-properties-common iotop p7zip-full audacious flatpak gimp

# ios device plug and play
sudo apt install usbmuxd libimobiledevice6 libimobiledevice-utils

# Install dependencies for R and RStudio
sudo apt install libxml2-dev libicu-dev zlib1g-dev make pandoc libcurl4-openssl-dev
sudo apt install libclang-dev libpq5

#----------------------------------------------------------------------
# Install other repository software
#----------------------------------------------------------------------
# Repos
## KeepassXC
sudo add-apt-repository ppa:phoerious/keepassxc
## mpv
sudo add-apt-repository ppa:mc3man/mpv-tests
## Inkscape
sudo add-apt-repository ppa:inkscape.dev/stable
## sublime text
wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/sublimehq-archive.gpg > /dev/null
echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list

# Install
sudo apt update
sudo apt install keepassxc mpv inkscape sublime-text

#----------------------------------------------------------------------
# Cleanup
#----------------------------------------------------------------------
sudo apt update
sudo apt full-upgrade
sudo apt autoclean
sudo apt autoremove

Manual packages

    Install rig

    rig automatically installs pak in the user library. pak is nice because it installs R packages as binaries instead of from source. However, OS package dependencies are installed in the background using sudo, and we need to allow a graphical interface to insert the password. So we solve that by running:

    sudo apt install ssh-askpass ssh-askpass-gnome

    then append to the file /etc/sudo.conf

    # append to /etc/sudo.conf
    Path askpass /usr/bin/ssh-askpass

    Each OS package dependency is executed in a seperate process, which means each process requires its own password authentication. We need to add a global sudo time limit for all processes.

    sudo visudo -f /etc/sudoers.d/timestamp_type

    then paste in the following text:

    # specify the timeout type (usual default=tty)
    Defaults:USERNAME timestamp_type=global

    # specify the timeout interval (usual default=15)
    Defaults:USERNAME timestamp_timeout=2

    Finally, we install rig:

    `which sudo` curl -L https://rig.r-pkg.org/deb/rig.gpg -o /etc/apt/trusted.gpg.d/rig.gpg
    `which sudo` sh -c 'echo "deb http://rig.r-pkg.org/deb rig main" > /etc/apt/sources.list.d/rig.list'
    `which sudo` apt update
    `which sudo` apt install r-rig

    and then install R

    rig add release

    and can use pak::pkg_install() without any issues.

    Install GnuCash

    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

    flatpak install flathub org.gnucash.GnuCash

    # uninstall
    #flatpak uninstall org.gnucash.GnuCash

    # Update stock quotes
    # https://wiki.gnucash.org/wiki/Flatpak
    flatpak run --command=gnucash-cli org.gnucash.GnuCash --quotes get /path/to/file.gnucash

    Install texlive 2022

    Reference http://tex.stackexchange.com/a/95373.

        Run

        sudo apt install wget perl-tk

        wget http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
        tar -zxvf install-tl-unx.tar.gz
        cd install-tl*
        sudo ./install-tl --gui

            Choose the small scheme (just download fonts and packages as you need them)
            Choose Recommended fonts, Mathematics packages, and LuaTeX packages
            Make sure to “create symlinks in system directories”

        Run following from the shell. It will add the lines to /etc/environment. Or add to ~/.profile manually.

        export MANPATH="$MANPATH:/usr/local/texlive/2022/texmf-dist/doc/man"
        export INFOPATH="$INFOPATH:/usr/local/texlive/2022/texmf-dist/doc/info"
        export PATH=/usr/local/texlive/2022/bin/x86_64-linux:$PATH

        Make apt see the local install by:

        sudo apt install equivs --no-install-recommends
        sudo apt install freeglut3
        mkdir /tmp/tl-equivs
        cd /tmp/tl-equivs
        equivs-control texlive-local
        # copy this http://www.tug.org/texlive/files/debian-equivs-2022-ex.txt to
        mousepad texlive-local
        equivs-build texlive-local
        sudo dpkg -i texlive-local_2022-1_all.deb
        sudo apt install -f

        Access tlmgr using sudo tlmgr --gui

        Update texlive. Remove the old texlive with the commands below, then Re-run the install commands.

        # Remove old apt local install
        sudo apt remove texlive-local

        # Remove the old texlive directories
        sudo rm -rf /usr/local/texlive/2022/
        sudo rm -rf /usr/local/texlive/texmf-local/
        sudo rm -rf ~/.texlive2022/
        sudo rm -rf /var/lib/texmf/

        # Remove the old texlive symlinks (Make sure there's nothing else in there)
        sudo rm /usr/local/bin/*
        sudo -rf rm /usr/local/share/man/*
        sudo rm /usr/local/share/info/*

        # Update the font cash
        sudo fc-cache -fsv

    Install Redshift

        Install from repo

        sudo apt-get install redshift redshift-gtk

        Append the following to geoclue’s config with sudo nano /etc/geoclue/geoclue.conf

        [redshift]
        allowed=true
        system=false
        users=

        Create a redshift config file with nano ~/.config/redshift.conf

        [redshift]
        temp-day=5500
        temp-night=2700
        location-provider=manual

        [manual]
        lat=4X
        lon=-8X

        Alternative software
            https://sr.ht/~kennylevinsen/wlsunset/
            https://gitlab.com/chinstrap/gammastep

    Modify sublime text’s settings
        At Preferences -> Distraction Free, add the line "update_check": false,
        Add 127.0.0.1 license.sublimehq.com to /etc/hosts.

    Install Rstudio

    Download from https://posit.co/download/rstudio-desktop/

    sudo dpkg -i *.deb
    sudo apt install -f

    Install Teamviewer

    Download from https://www.teamviewer.com/en/download/linux/

    sudo dpkg -i *.deb
    sudo apt install -f

    Install Anydesk

    Download from https://anydesk.com/download?os=linux

    sudo dpkg -i *.deb
    sudo apt install -f

    Anydesk uses a dark pattern of forcing autostart of a background service/system tray icon. To stop it, you needed to delete the following file:

    /etc/systemd/system/anydesk.service

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

Published: 2022-12-09
Last Updated: 2023-05-01

