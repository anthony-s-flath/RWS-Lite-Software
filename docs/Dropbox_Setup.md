# Dropbox Setup

Dropbox is used to transfer files between remote stations and the main database system. 

## Rclone

The `rclone` software is a command-line software tool that allows you to interface with Google Drive, Dropbox, and other cloud storage services. Learn more on their [website](https://rclone.org/).

To install the most recent version of `rclone`, run:

```
curl https://rclone.org/install.sh | sudo bash
```

Make sure you have version 1.55+:
```
rclone --version
```

Then, to connect your Dropbox account, you need to initialize a new `rclone` remote. To do this, execute the following:

```
rclone config
```

This will guide you through the setup process. First, type `n` and press enter to create a new remote. This will then prompt you to enter a name. 

Afterwards, you will be prompted to enter the type of storage service. You should look through the listed options for the number corresponding to "Dropbox," for example:
```
11 / Dropbox
   \ "dropbox"
```

You can leave the remaining prompts as their default options.

Finally, when asked if the change is ok, select "Yes" by typing in `Y` to save the remote.

### (Optional) Rclone on systems without a GUI

If you are using some type of remote access via ssh to the device, you will want to follow the above steps until `rclone` asks you about using autoconfiguration. You should select the "No" option and proceed to use another device to connect your dropbox accoun as instructed.