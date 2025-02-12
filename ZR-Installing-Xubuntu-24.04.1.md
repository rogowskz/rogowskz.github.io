
[Brett Klamer: The Complete Installation Guide for Xubuntu 22.04 (local copy)](Brett-Klamer-The-Complete-Installation-Guide-for-Xubuntu-22.04-local-copy)

## Installing on: zr-ThinkPad-T480:
2025-02-06

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

* Boot target computer from USB:
    * Insert USB
    * Enter BIOS setup:
        * Force shut down: Hold <Power> down for a few seconds.
        * Power up, press <Enter> when prompted on the ThikPad startup screen.
    * Select <F12> to select temporary boot media.

```bash
# Make sure you are using UEFI on the computer:
[ -d /sys/firmware/efi ] && echo "EFI boot" || echo "Legacy boot".
```

```bash
# Find HD size:
lsblk

sda 238.5 G

# Partitioning and LUKS enctypting:

# Identify installation device:
sudo -i # switch to root user
lsblk # determine the target drive

# Partitioning:
export DEV="/dev/sda" # save reference to drive location
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

# reboot
export DEV="/dev/sda" # save reference to drive location
sgdisk --print $DEV # after rebooting, to check all new partitions

# LUKS encrypt:
export DEVP="${DEV}" # save reference to base partition name
cryptsetup luksFormat --type=luks1 ${DEVP}1 # for the /boot/ partition
# podaj hasło.

cryptsetup luksFormat ${DEVP}5 # for the OS partition
# podaj hasło.

# LUKS unlock:
export DM="${DEV##*/}" # save reference to encrypted device mapper (without leading /dev/)
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


--------------------------------------------
[ZR Installing Xubuntu 22.04](ZR-Installing-Xubuntu-22.04)

```bash
# Partitions on T450s:
sda                      8:0    0 238.5G  0 disk  
├─sda1                   8:1    0   768M  0 part  
│ └─LUKS_BOOT          252:4    0   766M  0 crypt /boot
├─sda2                   8:2    0     2M  0 part  # bios_boot GRUB Core
├─sda3                   8:3    0   128M  0 part  /boot/efi # EFI System Partition
├─sda5                   8:5    0   119G  0 part  
│ └─sda5_crypt         252:0    0   119G  0 crypt 
│   ├─vgxubuntu-swap_1 252:1    0     8G  0 lvm   [SWAP]
│   ├─vgxubuntu-home   252:2    0     8G  0 lvm   /home
│   └─vgxubuntu-root   252:3    0  82.4G  0 lvm   /var/snap/firefox/common/host-hunspell
│                                                 /
└─sda6                   8:6    0 118.6G  0 part  
  └─veracrypt1         252:5    0 118.6G  0 dm    /media/veracrypt1
sdb                      8:16   1 119.5G  0 disk  
└─sdb1                   8:17   1 119.5G  0 part  
```

--------------------------------------------

The partitioning scheme:

```txt
+-------------------------++-----------++-----------++---------------------------+
|                         ||           ||           || Logical volume1 XX GB     |
|                         ||           ||           || /dev/mapper/vgxubuntu-root|
| 2 GB                    ||           || 128 MB    ||_ _ _ _ _ _ _ _ _ _ _ _ _ _|
| dm-crypt LUKS LVM       || 2 MB      || EFI       || dm-crypt LUKS LVM         | 
| /dev/mapper/LUKS_BOOT   || bios_boot || System    || /dev/mapper/sda5_crypt    |
|_ _ _ _ _ _ _ _ _ _ _ _ _|| GRUB Core || Partition || _ _ _ _ _ _ _ _ _ _ _ _ _ |
| dm-crypt LUKS partition ||           ||           || dm-crypt LUKS encrypted   |
| /dev/sda1               || /dev/sda2 || /dev/sda3 || /dev/sda5                 |
+-------------------------++-----------------------------------------------------+
```

Install Xubuntu 22.04 with dm-crypt LUKS encryption for all partitions

    Follow directions from https://help.ubuntu.com/community/Full_Disk_Encryption_Howto_2019 for full partition encryption.

        Open the terminal

        #----------------------------------------------------------------------
        # Identify installation device
        #----------------------------------------------------------------------
        # Switch to root user.
        sudo -i

        # Determine the target drive location.
        lsblk

        # Save shortcut reference to drive location (non-NVME drive).
        #export DEV="/dev/sda"

        # Save shortcut reference to drive location (NVME drive).
        export DEV="/dev/nvme0n1"

        # Shortcut reference to encrypted device mapper without leading `/dev/`.
        export DM="${DEV##*/}"

        # NVME devices need a 'p' before partition number. i.e. "nvme0n1p1".
        export DEVP="${DEV}$( if [[ "$DEV" =~ "nvme" ]]; then echo "p"; fi )"
        export DM="${DM}$( if [[ "$DM" =~ "nvme" ]]; then echo "p"; fi )"

        #----------------------------------------------------------------------
        # Partitioning
        #----------------------------------------------------------------------
        # Check for pre-existing partitions.
        sgdisk --print $DEV

        # ***If safe to delete all partitions***
        #sgdisk --zap-all $DEV

        # If anything goes wrong, check Gparted or `fdisk -l $DEV`.
        sgdisk --new=1:0:+2G $DEV
        sgdisk --new=2:0:+2M $DEV
        sgdisk --new=3:0:+128M $DEV
        sgdisk --new=5:0:0 $DEV
        sgdisk --typecode=1:8301 --typecode=2:ef02 --typecode=3:ef00 --typecode=5:8301 $DEV
        sgdisk --change-name=1:/boot --change-name=2:GRUB --change-name=3:EFI-SP --change-name=5:rootfs $DEV
        sgdisk --hybrid 1:2:3 $DEV

        #----------------------------------------------------------------------
        # LUKS Encryption
        #----------------------------------------------------------------------
        # Make sure to use luks version 1 on /boot/ since GRUB requires it.
        cryptsetup luksFormat --type=luks1 ${DEVP}1

        # Set up LUKS on the system partition.
        cryptsetup luksFormat ${DEVP}5

        #  Open the encrypted devices.
        cryptsetup open ${DEVP}1 LUKS_BOOT
        cryptsetup open ${DEVP}5 ${DM}5_crypt
        ls /dev/mapper/

        #----------------------------------------------------------------------
        # Format file systems
        #----------------------------------------------------------------------
        mkfs.ext4 -L boot /dev/mapper/LUKS_BOOT
        mkfs.vfat -F 16 -n EFI-SP ${DEVP}3

        #----------------------------------------------------------------------
        # LVM Logical Volume Manager
        #----------------------------------------------------------------------
        # Naming scheme for different releases of ubuntu
        flavour="$( sed -n 's/.*cdrom:\[\([^ ]*\).*/\1/p' /etc/apt/sources.list )"
        release="$( lsb_release -sr | tr -d . )"
        if [ ${release} -ge 2204 ]; then VGNAME="vg${flavour,,}"; else VGNAME="${flavour}--vg"; fi 
        export VGNAME

        # Create Volumes
        pvcreate /dev/mapper/${DM}5_crypt
        vgcreate "${VGNAME}" /dev/mapper/${DM}5_crypt
        # If you want a swap partition/volume
        #lvcreate -L 1G -n swap_1 "${VGNAME}"
        lvcreate -l 80%FREE -n root "${VGNAME}"

        Keep terminal open, but switch back to proceeding with installation.

    Installer main menu

        Keyboard layout
            English (US)

        Updates and other software
            Download updates while installing Xubuntu
            Install third-party software

        Installation type
            Something else
                Select the root file-system device for formatting (/dev/mapper/vgxubuntu-root), press the Change button, choose Use As Ext4 and Mount point /.
                If you created a swap volume: Select the swap device (/dev/mapper/vgxubuntu-swap_1), press the Change button, choose Use as swap area.
                Select the Boot file-system device for formatting (/dev/mapper/LUKS_BOOT), press the Change button. choose Use as Ext4… and Mount point /boot
                Select the boot-loader device (/dev/nvme0n1p1 for example). Boot-loader device should always be a raw disk not a partition or device-mapper node.
                Press the Install Now button to write the changes to the disk and press the Continue button.

        Where are you

        Who are you
            After finishing this step, immediately perform next step. The next step needs to be run before installation is finished in the background?

        Open the terminal
            while [ ! -d /target/etc/default/grub.d ]; do sleep 1; done; echo "GRUB_ENABLE_CRYPTODISK=y" > /target/etc/default/grub.d/local.cfg
                Check file for successful addition of text.

        After successful installation, choose continue testing.

        Open the terminal

        #-----------------------------------------------------------------------
        # Change-root environment to work in the newly installed OS
        #-----------------------------------------------------------------------
        mount /dev/mapper/${VGNAME}-root /target
        for n in proc sys dev etc/resolv.conf; do mount --rbind /$n /target/$n; done
        chroot /target
        mount -a

        #-----------------------------------------------------------------------
        # Configure cryptsetup-initramfs and key file
        #-----------------------------------------------------------------------
        apt install -y cryptsetup-initramfs

        # Note that since we chroot'd to `/target` the following changes will be
        # made in the files at the /target path.
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

        # Update the initialramfs files to add the cryptsetup unlocking scripts and the key-file
        update-initramfs -u -k all

    Reboot the computer and remove installation media. You should be asked for the password at GRUB.

Post install options

    Set audio/sound/volume level using keyboard shortcuts.

    In Settings -> Keyboard -> Application Shortcuts, click add, then insert

    amixer -D pulse set Master 5%+
    amixer -D pulse set Master 5%-
    amixer -D pulse set Master toggle

    Set window tile keybinds.
        Open terminal and run
            xfce4-settings-manager
        Go to window manager
            Open the Keyboard tab
                Set the “Tile window to the left” (and right)

    Set backbutton in firefox to backsapce.
        Type about:config in the address bar
        Look for browser.backspace_action in the list
        Change the Value to 0.

    Change desktop lock keybind.
        Go to settings editor
        xfce4-keyboard-shortcuts
        new commands custom property
            property: /commands/custom/<super>l
            type: string
            value: xflock4

    Fix laptop screen brightness steps

    In Settings -> Power Manager -> General, there is an option for “Brightness step count”. Increase this to a value such as 20.

    Otherwise, tools such as acpilight, light, and xbacklight may be of help. If you sudo make install acpilight, then you will need to run sudo usermod -a -G video USERNAME so that sudo is not required to execute xbacklight. You can then bind the command to a key combo under Settings -> Keyboard -> Application Shortcuts.

    Enable the firewall.

    # https://help.ubuntu.com/community/UFW
    # https://www.linode.com/docs/security/firewalls/configure-firewall-with-ufw/
    sudo ufw enable
    sudo ufw default deny outgoing
    sudo ufw default deny incoming

    sudo ufw allow out to any port 80
    sudo ufw allow out to any port 443
    sudo ufw allow out to any port 53

    # additional ports to allow out
    # https://www.cups.org/doc/firewalls.html
    # brother printer: 54925, 54926, 137, 161

    sudo ufw reload
    sudo ufw status verbose

    # If anything goes wrong, you can reset ufw
    #sudo ufw --force reset

    Edit the hosts file
        Grab the hosts file from https://github.com/StevenBlack/hosts
        paste into /etc/hosts

    Update the Linux kernel.
        If you want a specific kernel
            Download the following from http://kernel.ubuntu.com/~kernel-ppa/mainline/
                linux-headers-5.*-generic_*_amd64.deb
                linux-headers-5.*_all.deb
                linux-image-unsigned-5.*-generic_*_amd64.deb
                linux-modules-5.*-generic_*_amd64.deb
            Open terminal in download location and run
                sudo dpkg -i linux-headers*.deb
                sudo dpkg -i linux-modules*.deb
                sudo dpkg -i linux-image*.deb
                sudo update-grub
            Restart computer
            Check kernel being used with
                uname -a
            Remove old kernels if /boot gets full

    Check disk io/r/w transactions
        sudo iotop -oPa

    If there is a separate partition or disk that needs to be mounted and unencrypted at boot. Reference http://ubuntuforums.org/showthread.php?t=837416.
        Check UUID of partitioning
            sudo blkid
        Check block size of / (root) partition for nice key size (likely 4096)
            sudo blockdev --getbsz /dev/mapper/system-root
        Create random keyfile in /root
            sudo dd if=/dev/urandom of=/root/keyfile bs=4096 count=1
                the bs= value should be the block size we just found
        Make keyfile read only to root
            sudo chmod 0400 /root/keyfile
        Add keyfile to LUKS partition of /dev/sdX#_crypt
            sudo cryptsetup luksAddKey /dev/sdX#_crypt /root/keyfile
                Enter existing password for /dev/sdX#_crypt
        Create mapper
            sudo mousepad /etc/crypttab
            add ‘/root/keyfile’ to replace ’none’ for /dev/sdX#_crypt
                example: sdX#_crypt UUID=XXX /root/keyfile luks
        Mount the drive (if needed)
            sudo mousepad /etc/fstab
                example: /dev/mapper/sdX#_crypt /<mount point> btrfs relatime 0 2
        Update settings in initramfs images
            sudo update-initramfs -u -k all

    TRIM for SSDs.
        Reference http://blog.neutrino.es/2013/howto-properly-activate-trim-for-your-ssd-on-linux-fstrim-lvm-and-dmcrypt/.
        Enable Trim on dm-crypt
            Open /etc/crypttab
                sudo mousepad /etc/crypttab
                If needed, add ‘discard’ to the options for sdX#_crypt.
        Make sure LVM has ‘issue_discards=1’ in
            sudo mousepad /etc/lvm/lvm.conf
        Check encrypted drive with
            sudo dmsetup table /dev/mapper/sdX#_crypt
            make sure it has ‘1 allow_discards’
        Remove or check “discard” is not used in the fstab
            sudo mousepad /etc/fstab
        Run TRIM manually or check for errors
            sudo fstrim -v /home
        If any changes were made, run
            sudo update-initramfs -c -k all

    If installing in Virtualbox, install additions by
        sudo apt install virtualbox-guest-utils virtualbox-guest-dkms dkms
        To share a folder, make a permanent machine folder then run
            sudo usermod -a -G vboxsf username
        To share a USB port
            sudo usermod -a -G vboxusers username

    If needed, install Intel wireless driver.
        Download driver from http://intellinuxwireless.org/?n=Downloads
        Navigate to download folder
            tar xvzf iwlwifi-XXX.tgz
            cd iwlwifi-XXX/
            sudo cp iwlwifi-XXX.ucode /lib/firmware

    Check partition sizes.
        df -h

    Modify or redirect home folder names.
        change in /home/username/.config/user-dir.dirs

    Change ownership of extra storage drives or partitions.
        sudo chown -R username /partition

    Format a USB drive.
        df
        umount /dev/sdc1
        mkfs.vfat /dev/sdc1

    Create a dm-crypt LUKS encrypted external drive.

    Reference https://gitlab.com/cryptsetup/cryptsetup/wikis/FrequentlyAskedQuestions.

        Find the external drive (assume the filesystem is /dev/sdb1 and it’s mount location /media/USERNAME/*)

        df

        Unmount it

        umount /media/USERNAME/*

        Quickly wipe old filesystems. wipefs clears the first superblock.

        sudo wipefs -a /dev/sdb1

        Create the LUKS container (follow on-screen intructions)

        sudo cryptsetup luksFormat /dev/sdb1

        Check the passphrase iteration count. The key slot default is 1 second of PBKDF2 hashing. The volume key default (MK iterations) is 0.125 seconds. You can set the key slot with cryptsetup luksFormat -i 15000 <target device>

        sudo cryptsetup luksDump /dev/sdb1

        Map the container to /dev/mapper/backup1

        sudo cryptsetup luksOpen /dev/sdb1 backup1

        Create a filesystem in the mapped container

        sudo mkfs.btrfs --label backup1 /dev/mapper/backup1

        Mount the filesystem (right after creation; using lzo compression)

        mount -o compress=lzo /dev/mapper/backup1 /mnt

        Mount the filesystem (day to day use as a portable external drive; using lzo compression). You can either create an fstab entry or mount using the command line.

            Using an fstab entry

            # Get the UUID of the mounted and unlocked /dev/mapper/ filesystem
            sudo blkid

            Add the following entry to /etc/fstab

            UUID=YOUR-UUID /media/backup1 btrfs noauto,defaults,noatime,compress=lzo 0 0

            Now it will automatically mount at /media/backup1. The noauto option is used in the fstab entry to prevent automatically mounting the drive at boot time. If you leave this option off, then your computer will fail to boot and you will need to edit the fstab in recovery mode. The nofail option can be used for drives that are usually going to be mounted at boot time.

            Change ownership of the new mount point so you can perform cut/copy/paste, etc.

            sudo chown -R USERNAME /media/backup1

            Using the terminal

            # The OS will automatically mount the drive and ask for passphrase to unlock. Then...
            df
            sudo umount /media/USERNAME/*
            sudo mount -o compress=lzo /dev/dm-4 /media/backup1
            sudo chown -R USERNAME /media/backup1

    Stop system error pop ups.

    Sometimes a system error will be reported and cause a warning pop up over multiple restarts. You can remove this by either
        sudo rm /var/crash/*
        gksu nano /etc/default/apport and set enabled=0

    Randomize MAC address.

    This is based on https://fedoramagazine.org/randomize-mac-address-nm/. To randomize wifi connections, create the file /etc/NetworkManager/conf.d/00-macrandomize.conf and add the following:

    # can use 'random' or 'stable' below
    [device]
    wifi.scan-rand-mac-address=yes

    [connection]
    wifi.cloned-mac-address=stable
    ethernet.cloned-mac-address=stable
    connection.stable-id=${CONNECTION}/${BOOT}

    Then restart networkmanager with systemctl restart NetworkManager.

    Change owner of entire directory.

    sudo chown -R <username> *

    Let apt fix dependency issues automatically.

    sudo apt --fix-broken install

    GPG bug fix when adding keys behind a proxy: use the option http-proxy=

    sudo apt-key adv --keyserver keyserver.ubuntu.com --keyserver-options http-proxy=http://PROXYADDRESS --recv-keys GPGKEY

    Fix bluetooth audio stuttering.

    Open a terminal and run

    sudo mousepad /etc/bluetooth/audio.conf

    Then add the following text to the new file:

    [General]
    Enable=Source,Sink,Media,Socket

    Finally, restart the bluetooth service

    sudo service bluetooth restart

    Fix bluetooth audio not working.

    Open a terminal and run

    lsmod | grep btusb
    sudo rmmod btusb
    lsmod | grep btusb
    sudo modprobe btusb
    lsmod | grep btusb
    bluetoothctl
    scan on

    Fix QT scaling for hidpi displays.

    Open ~/.profile and append

    export QT_SCALE_FACTOR=2

Software install suggestions
Apt packages

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

