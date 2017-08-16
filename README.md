Better Brenda
=============

This is a personal fork of jamesyonan's Brenda and rider-rebooted's win_brenda_console. 

While both of these utilities make it relatively easy to use AWS EC2 instances for Blender rendering, there were certain features that were required for my workflow that neither project provided.

Here are the changes:

* **Choose an AWS availability zone:** The original Brenda script provided no way to choose an availability zone for spot market instances. If you don't supply an availability zone, AWS automatically picks one for you -- which may not be the cheapest zone for spot market instances. With this fork, a specific AWS availability zone can be selected on the Brenda side as well as in win_brenda_console. win_brenda_console will ask which Availability Zone you would like when setting up your render farm. Note that win_brenda_console currently hardcoded for us-east-1 (the geographic area that I use). If you need to change this, change the value for the variable "zonebase" in win_brenda_console.py.

* **Upload a Blender project PLUS external artwork files:** I typically utilize external artwork files such as image sequences that are not possible to pack into the .blend file. As long as you upload a .zip file with the .blend file and all of the associated external files in the proper relative locations (and have "Make All Paths Relative" turned on in your Blender file), Brenda will faithfully render your .blend file with the external artwork files. However, win_brenda_console only supports sending .zip files with the .blend file and no external files. To rectify this, there is a new menu under Setting up your farm/Project:

```
b = Upload .blend file
e = Upload .blend file plus external artwork files
z = Upload already zipped archive
```

"Upload .blend file" operates with win_brenda_console's original behavior, which is to take a single .blend file, zip it, and upload it to the S3 bucket. 

"Upload .blend file plus external artwork files" will zip up a .blend file plus everything in the relative directory "/artwork/in project" from the .blend file and upload it to the S3 bucket. This is the standard path I use in my Blender projects, as it allows me to have the paths "/artwork/not in project" (for files that were used to create the artwork in the "in project" directory) and "/artwork/in project (local only)" (for files that are part of the Blender project but should not be uploaded to AWS, like audio files and video overlay files).

"Upload already zipped archive" is intended to be used in two different cases:

1. You have a .blend file that relies upon locations that are outside of "/artwork/in project". For example, if you create a water simulation, Blender will place all of the water simulation files in a directory named "cache_fluid_XXXX" at the same directory level as your project file. In this scenario, you will want to manually zip up all of the files that you need and then upload it to your S3 bucket.
2. You already have a large zipped archive in your S3 project directory and do not wish to re-zip and re-upload it.

If you pick the "Upload already zipped archive" option, you still must select the zipped archive to upload. win_brenda_console simply uses that file name to determine what file name value to send to Brenda. win_brenda_console does not re-zip, resend, or delete the zip file with this option.

* **Longer time to read messages:** win_brenda_console had a 2 second delay to read messages, and sometimes these messages were long error messages which could not be read quickly. Now there are frequent "Press Enter to continue" messages so you have a chance to fully read (or copy) the messages on the screen. For very short confirmation messages, there is now a 3 second delay.

* **"--enable-autoexec" added to the frame and subframe template:** The Blender command line flag "--enable-autoexec" has been added to the frame and subframe template. This is the equivalent of going into Blender User Preferences->File and checking "Auto Execution: Auto Run Python Scripts". If this option is not turned on and you are using BlenRig, the armature won't run correctly (FK arms and forearms will stay completely straight).

* **Error message if not connected to the internet:** Instead of crashing at the beginning of the script, win_brenda_console will display the warning message, "There was a problem setting up the application. Is this computer connected to the internet?" before continuing to the initial menu.

Additional Notes
----------------

* It is assumed that you have already installed and successfully run the original win_brenda_console application before trying this fork. In order to run this modified version of win_brenda_console, you must add a line to your .brenda.conf file before running this for the first time, otherwise you will encounter an error:

```
AVAILABILITY_ZONE=us_east-1c
````
