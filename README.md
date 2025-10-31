# connection-specific-ssh-config

The Linux SSH client has many configuration options to choose from, and sometimes you may find yourself wishing you could automatically change certain options depending on what network you're connected to (ie: home, work, school, etc).

**connection-specific-ssh-config** is a simple script written in python, which can change your ssh configuration file (usually found in ~/.ssh/config) depending on what network you're currently connected to.

Written by Mike Peralta and released to the public via GPLv3 on Sunday, May 27th, 2018

## Requirements

  * Linux (possibly others)

  * Python 3

    * pyenv

    * pipenv

  * NetworkManager and nmcli (tested on v1.46)

  * One of the following: root access, the ability to place executable files inside NetworkManager's dispatcher directory, or the ability to call this script whenever connection details change

Note: This script has only been tested with NetworkManager and nmcli 1.46, but should work with any other daemon or application that can call this script with the required parameters.

You can also try using this script with a different daemon (or your own custom script). All you need to do is call this script whenever some change in the network occurs, with the following parameters:

```bash
$ cd path/to/connection-specific-ssh-config && pipenv run python main.py --config <config_path> --adapter <adapter> --command <command>
```

  * Where *config_path* is the path to a yaml configuration file, explained below

  * Where *adapter* is the name of the adapter/interface that has changed states

  * Where *command* is the type of change occurring. Currently, the script only does anything when receiving the `up` command.


## Installation (NetworkManager)

This section to help with installation.

### Python Environment

  1. Install [pyenv](https://github.com/pyenv/pyenv)
  2. Install [pipenv](https://pipenv.pypa.io/en/latest/)

Setting up the *pipenv* environment is pretty straight forward:

```bash
$ cd /path/to/connection-specific-ssh-config
$ pyenv update
$ pyenv install
$ pip install --upgrade pip pipenv
$ pipenv sync
```

You should then be able to get a help menu with:

```bash
$ cd /path/to/connection-specific-ssh-config
$ pipenv run python main.py --help
```

### SSH Config Preparation

1. Move your old ssh configuration file (typically at *~/.ssh/config*) to a safe backup, like:

    * ```mv ~/.ssh/config config-backup```

2. Create as many customized ssh configuration files as you need, such as `config-remote` or `config-home`. Do not name any of them `config`.

### Configuration File

1. Create a configuration file somewhere safe, such as ```/path/to/connection-specific-ssh-config.yaml``` (explained in detail further below)

### Network Manager Dispatch

1. Open a terminal and navigate to NetworkManager's dispatcher directory, often found here:

    * ```cd /etc/NetworkManager/dispatcher.d```

    * There may be subdirectories underneath. Just ignore them.

2. Create a short bash script inside the dispatcher directory that will launch *connection-specific-ssh-config*. For instance, you might name this file ```/etc/NetworkManager/dispatcher.d/99-launch-connection-specific-ssh-config```

3. Inside your launcher script, put the following contents:

        #!/bin/bash

        cd /path/to/connection-specific-ssh-config && pipenv run python main.py --config /path/to/your/config.yaml --interface "$1" --command "$2"

    * This will take the two important variables which NetworkManager has passed along to your launcher script, and give them to *connection-specific-ssh-config*

4. Repeat steps  1-3 for each additional user who would like connection based ssh configuration files.

## Example Scenarios

Why would you use this script? Suppose the following scenarios:

* You have various servers you connect to when at work, which have long server names. You might put host aliases inside your laptop's SSH configuration file (at ~/.ssh/config) to speed up your ssh commands. But when you come home, you don't want those shortcuts anymore. Thus, you need one ssh configuration file for work, and another for home

* One of your work locations has very slow internet, so whenever you're there, you need to change several SSH configuration options (such as ServerAliveInterval, and others), so you can work more efficiently there.

* You have several servers which you can connect directly to from work. Your work has no VPN, so when at home, these servers aren't exactly online; You must first connect to a gateway server on your employer's network, then use that gateway server as a proxy to reach the other internal servers. This is generally called Transparent Multihop over SSH ([example](http://sshmenu.sourceforge.net/articles/transparent-mulithop.html)). Thus, it would really be convenient to have one ssh configuration file for home, and one for work.

Each of these scenarios can be solved by the connection-specific-ssh-config script. Simply create as many ssh configuration files as you need, and each can be dynamically symlinked as you connec to different networks.

## Configuration File
Configuration files for connection-specific-ssh-config are written in YAML and are relatively simple:

* You need a section called `options`, which holds two variables:

    1. `ssh-dir`, which specifies your ssh configuration directory (typically *~/.ssh/*)
    2. `default-target`, which specifies the default target to use if the currently connected wifi access point does not match anything configured.

* You then need one or more sections which specify targets that associate ssh configuration files with network connection names:

    * The key `adapter` can specify one adapter to watch
    * The key `adapters` can specify multiple adapters, as a list
    * The key `ssid` can specify one connection name
    * The key `ssids` can specify multiple connection names, as a list
    * The key *config-file-name* specifies the name of the ssh configuration file that should apply if this target activates

Here's an example configuration file to help you get started:

```yaml
options:

  default-target: remote
  ssh-dir: /home/your-username/.ssh

targets:

  home:
    adapters:
      - wlo1
    ssids:
      - Some Wifi AP Name
      - Some Other Wifi AP Name
    config-file-name: config-home

  remote:
    adapters:
      - wlo1
    config-file-name: config-remote
```

The above configuration file will instruct the script to use the ssh config file */home/your-username/.ssh/config-home* while you're connected to one of the access points named in the `ssids` list of the `home` target. Otherwise, the default config file */home/your-username/.ssh/config-remote* would be used. All of this would only apply to the adapter `wlo1`, but you could specify more adapters.

The script works by simply creating a symlink where your original ssh configuration file was (typically *~/.ssh/config*), pointing to the ssh configuration determined to be the one you want active. Note that this of course means the script will fail (for safety reasons), if your original ssh configuration file still exists as a normal file.


