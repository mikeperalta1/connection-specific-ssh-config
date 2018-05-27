# connection-specific-ssh-config

The Linux SSH client has many configuration options to choose from, and sometimes you may find yourself wishing you could automatically change certain options depending on what network you're connected to (ie: home, work, school, etc).

**connection-specific-ssh-config** is a simple script written in python, which can change your ssh configuration file (usually found in ~/.ssh/config) depending on what network you're currently connected to.

Written by Mike Peralta and released to the public via GPLv3 on Sunday, May 27th, 2018

## Requirements
* Linux (possibly others)
* Python 3
* NetworkManager and nmcli (tested on v1.10.6)
* One of the following: root access, the ability to place executable files inside NetworkManager's dispatcher directory, or the ability to call this script whenever connection details change

Note: This script has only been tested with NetworkManager and nmcli 1.10.6, but should work with any other daemon or application that can call this script with the required parameters.

You can also try using this script with a different daemon (or your own custom script). All you need to do is call this script whenever some change in the network occurs, with the following parameters:

```connection-specific-ssh-config <interface> <command> <ini_path>```

* Where *interface* is the name of whatever interface just changed
* Where *command* is the type of change occurring. Currently, the script only does anything when receiving the "up" command.
* Where *ini_path* is the path to an ini configuration file, explained below

## Installation (NetworkManager)
1. Copy this script somewhere safe, such as ```/path/to/connection-specific-ssh-config```

2. Move your old ssh configuration file (typically at *~/.ssh/config*) to a safe backup, like:

   ```mv ~/.ssh/config config-backup```

3. Create as many customized ssh configuration files as you need

4. Create a configuration file somewhere safe, such as ```/path/to/connection-specific-ssh-config.ini``` (explained in detail further below)
   
5. Open a terminal and navigate to NetworkManager's dispatcher directory, often found here:

   ```cd /etc/NetworkManager/dispatcher.d```

6. Create a short bash script inside the dispatcher directory that will launch connection-specific-ssh-config. For instance, you might name this file ```/etc/NetworkManager/dispatcher.d/99-launch-connection-specific-ssh-config```

7. Inside your launcher script, put the following contents:

  ```
  #!/bin/bash
  
  /path/to/connection-specific-ssh-config "$1" "$2" "/path/to/connection-specific-ssh-config.ini"
  ```
  
  This will take the two important variables which NetworkManager has passed along to your launcher script, and pass them along to connection-specific-ssh-config

8. Repeat steps  2-7 for each additional user who would like connection based ssh configuration files.

## Example Scenarios

Why would you use this script? Suppose the following scenarios:

* You have various servers you connect to when at work, which have long server names. You might put host aliases inside your laptop's SSH configuration file (at ~/.ssh/config) to speed up your ssh commands. But when you come home, you don't want those shortcuts anymore. Thus, you need one ssh configuration file for work, and another for home

* One of your work locations has very slow internet, so whenever you're there, you need to change several SSH configuration options (such as ServerAliveInterval, and others), so you can work more efficiently there.

* You have several servers which you can connect directly to from work. Your work has no VPN, so when at home, these servers aren't exactly online; You must first connect to a gateway server on your employer's network, then use that gateway server as a proxy to reach the other internal servers. This is generally called Transparent Multihop over SSH ([example](http://sshmenu.sourceforge.net/articles/transparent-mulithop.html)). Thus, it would really be convenient to have one ssh configuration file for home, and one for work.

Each of these scenarios can be solved by the connection-specific-ssh-config script. Simply create as many ssh configuration files as you need, and each can be dynamically symlinked as you connec to different networks.

## Configuration File
Configuration files for connection-specific-ssh-config are just standard python/php style ini files, and are relatively simple:

* You need a section called "config", which currently only holds one variable:
   * *ssh_dir*, which specifies the directory your ssh client looks for configuration files (typically *~/.ssh/*)

* You then need one or more sections which specify targets that associate ssh configuration files with network connection names
   * The key *adapter* can specify one adapter to watch
   * The key *adapters* can specify multiple adapters (must be written in JSON format)
   * The key *ssid* can specify one connection name
   * The key *ssids* can specify multiple connection names (must be written in JSON format)
   * The key *ssh_config_name* specifies the name of the ssh configuration file that should apply if this target activates

* You can then optionally add a "default" section, which specifies which default ssh configuration file to fallback to, if any

Here's an example configuration file to help you get started:

```

[config]
ssh_dir = /home/mike/.ssh

[default]
adapter = wlan0
ssh_config_name = config-default

[Wifi Work]
adapters = ["wlan0", "wlan1"]
ssids = ["Work Connection - Main Office", "Work Connection - Garys Office"]
ssh_config_name = config-work

[Wifi Home]
adapter = wlan0
ssid = My Home Connection (Oh Joy)
ssh_config_name = config-home

```

The above configuration file will instruct the script to use the ssh configuration file */home/mike/.ssh/config-work* while you're connected to one of your work connections *Work Connection - Main Office* or *Work Connection - Garys Office*, on either of your wireless adapters *wlan0* or *wlan1*. When you get home and connect to your *My Home Connection (Oh Joy)* connection on *wlan0*, the config file */home/mike/.ssh/config-home* will be used instead. Finally, the configuration file */home/mike/.ssh/config-default* will be used when *wlan0* connects to some undefined network.

The script works by simply creating a symlink where your original ssh configuration file was (typically *~/.ssh/config*), pointing to the ssh configuration determined to be the one you want active. Note that this of course means the script will fail (for safety reasons), if your original ssh configuration file still exists as a normal file.


