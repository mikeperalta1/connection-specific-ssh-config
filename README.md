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
2. Create a configuration file somewhere safe, such as ```/path/to/connection-specific-ssh-config.ini``` (explained in detail further below)
3. Open a terminal and navigate to NetworkManager's dispatcher directory, often found here:

   ```cd /etc/NetworkManager/dispatcher.d```
4. Create a short bash script inside the dispatcher directory that will launch connection-specific-ssh-config. For instance, you might name this file ```/etc/NetworkManager/dispatcher.d/99-launch-connection-specific-ssh-config```
5. Inside your launcher script, put the following contents:
  ```
  #!/bin/bash
  
  /path/to/connection-specific-ssh-config "$1" "$2" "/path/to/connection-specific-ssh-config.ini"
  ```
  This will take the two important variables which NetworkManager has passed along to your launcher script, and pass them along to connection-specific-ssh-config

6. Repeat steps  2-5 for each additional user who would like connection based ssh configuration files.

## Example Scenario

Why would you use this script? Suppose the following scenarios:

* You have various servers you connect to when at work, which have long server names. You might put host aliases inside your laptop's SSH configuration file (at ~/.ssh/config) to speed up your ssh commands. But when you come home, you don't want those shortcuts anymore. Thus, you need one ssh configuration file for work, and another for home

* One of your work locations has very slow internet, so whenever you're there, you need to change several SSH configuration options (such as ServerAliveInterval, and others), so you can work more efficiently there.

* You have several servers which you can connect directly to from work. Your work has no VPN, so when at home, these servers aren't exactly online; You must first connect to a gateway server on your employer's network, then use that gateway server as a proxy to reach the other internal servers. This is generally called Transparent Multihop over SSH ([example](http://sshmenu.sourceforge.net/articles/transparent-mulithop.html)). Thus, it would really be convenient to have one ssh configuration file for home, and one for work.

