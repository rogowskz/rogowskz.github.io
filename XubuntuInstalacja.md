
# Post-installation operations:

## Set single-click items opening:

https://askubuntu.com/questions/880844/xubuntu-16-04-set-mouse-to-always-single-click

Single click to access items is done in two parts for Xfce. Your Desktop and File Manager are set separately.
For the Desktop: go to Applications > Settings > Desktop and in the Icons tab choose Single click to activate items.
For File Manager: Applications > System > Thunar File Manager , Edit > Preferences > Behavior > Navigation > Single click to activate items
Then in your Applications > Settings > File Manager in the Behavior tab, choose Single click to activate items and that should make it single click for you."

## Configure Terminal:

Default size, location, cursor, colors, ...

## Install Vim:

`sudo apt install vim`

## Install VeraCrypt:

[How to Install VeraCrypt on Ubuntu 22.04 or 20.04](https://www.linuxcapable.com/install-veracrypt-on-ubuntu-linux/)

## Create and mount a VeraCrypt volume in the dedicated partition:

ZR-HP-desktop: /dev/sda6

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
rsync -avW --delete ~/home /media/veracrypt1/ 

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

#########################################

## Install GitHub CLI:
https://cli.github.com/
    https://github.com/cli/cli/blob/trunk/docs/install_linux.md

```bash
type -p curl >/dev/null || (sudo apt update && sudo apt install curl -y)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
&& sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \
&& sudo apt install gh -y
```

#########################################

## Configure desktop Panel:
TODO: 

## Install ~/gdrive CLI utility:

## Configure GPG:
TODO: 

## Conect Brother printer - wireless:
TODO: 

## Clone ZR-HP-desktop - except /dev/sda6 partition:
TODO: 



