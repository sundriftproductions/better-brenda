Better Brenda
=============

This is a personal fork of jamesyonan's Brenda and rider-rebooted's win_brenda_console. 

While both of these utilities make it relatively easy to use AWS EC2 instances for Blender rendering, there were certain features that were required for my workflow that neither project provided.

Here are the main changes:

* **Choose an AWS availability zone:** The original Brenda script provided no way to choose an availability zone for spot market instances. If you don't supply an availability zone, AWS automatically picks one for you -- which may not be the cheapest zone for spot market instances. With this fork, a specific AWS availability zone can be selected on the Brenda side as well as in win_brenda_console. win_brenda_console will ask which Availability Zone you would like when setting up your render farm. Note that win_brenda_console currently hardcoded for us-east-1 (the geographic area that I use). If you need to change this, change the value for the variable "zonebase" in win_brenda_console.py.

* **Upload a Blender project PLUS external artwork files:** I typically utilize external artwork files such as image sequences that are not possible to pack into the .blend file. As long as you upload a .zip file with the .blend file and all of the associated external files in the proper relative locations (and have "Make All Paths Relative" turned on in your Blender file), Brenda will faithfully render your .blend file with the external artwork files. However, win_brenda_console only supports sending .zip files with the .blend file and no external files. To rectify this, there are some new menu settings under `Setting up your farm -> Project`:

```
b = Upload .blend file
e = Upload .blend file plus external artwork files
w = Upload .blend file with "good workflow" directory structure plus external artwork files
z = Upload already zipped archive
```

`Upload .blend file` operates with win_brenda_console's original behavior, which is to take a single .blend file, zip it, and upload it to the S3 bucket. 

`Upload .blend file plus external artwork files` will zip up a .blend file plus everything in the relative directory `/artwork/in project` from the .blend file and upload it to the S3 bucket. This an approach that I use in my Blender projects when I want to do something quick and dirty, as it allows me to have the paths `/artwork/not in project`(for files that are part of the Blender project but should not be uploaded to AWS, like audio files and video overlay files).

`Upload .blend file with "good workflow" directory structure plus external artwork files` is more complicated. This uploads a project that follows a directory structure that might be seen at a professional production house (such as Pixar or WETA). See the "Good Workflow Structure" section of this document on how to set up a project that uses "good workflow".

`Upload already zipped archive` is intended to be used in two different cases:

1. You have a .blend file that relies upon locations that are outside of `/artwork/in project`. For example, if you create a water simulation, Blender will place all of the water simulation files in a directory named `cache_fluid_XXXX` at the same directory level as your project file. In this scenario, you will want to manually zip up all of the files that you need and then upload it to your S3 bucket.
2. You already have a large zipped archive in your S3 project directory and do not wish to re-zip and re-upload it.

If you pick the `Upload already zipped archive` option, you still must select the zipped archive to upload. win_brenda_console simply uses that file name to determine what file name value to send to Brenda. win_brenda_console does not re-zip, resend, or delete the zip file with this option. It is expected that the .blend file is in the root directory of the zipped archive.

* **Longer time to read messages:** win_brenda_console had a 2 second delay to read messages, and sometimes these messages were long error messages which could not be read quickly. Now there are frequent "Press Enter to continue" messages so you have a chance to fully read (or copy) the messages on the screen. For very short confirmation messages, there is now a 3 second delay.

* **"--enable-autoexec" added to the frame and subframe template:** The Blender command line flag "--enable-autoexec" has been added to the frame and subframe template. This is the equivalent of going into Blender's `User Preferences -> File` and checking `Auto Execution: Auto Run Python Scripts`. If this option is not turned on and you are using BlenRig, the armature won't run correctly (FK arms and forearms will stay completely straight).

* **Removed the ability to pick a preconfigured AMI:** While it was convenient to pick a preconfigured AMI, the feature relied upon a download -- now removed -- from a web site to get this information. As a result, the original win_brenda_console project will crash upon starting as well as when trying to select an AMI. Since this is a somewhat advanced tool for rendering, it is assumed that you have build your own AMI for rendering.

* **Created more descriptive messages regarding frames, instances, and files:** The application provides hints regarding how many frames are selected to render, how many instances you might want to employ for a render, and how many files should be generated by the render.

* **Instance types have been updated:** c1.xlarge is removed because I never found it useful and it always cost way more than the c3 instances. c3.4xlarge was added because I needed more computing power.

* **Additional options for stopping the render farm and clearing out frames:** Under `Canceling and resetting your farm`, instead of having to always enter the combination r, Enter, s, Enter, c, Enter, e, Enter to reset the work queue, stop all running instances, cancel pending spot requests, and empty frame/project buckets, there is a new option to do all of these at once. There is also an option which omits the final step of emptying the frame/project buckets.

* **Additional options for selecting a frame range:** Under `Setting up your farm -> Frames`, the menu has two new options:

```
r = Use (and set) frame range
u = Use (and select) a frame list file (a text file containing a list of specific frames to render)
```

`Use (and set) frame range` works as setting a frame range worked in the original application, where you pick a start and end frame and Brenda will render everything between those two frame numbers (inclusive).

`Use (and select) a frame list file (a text file containing a list of specific frames to render)` means exactly what it says. If you only want to render a set of non-contiguous frames, you can create a text file that contains a list of them and then upload that file to the application. This is helpful if you have a handful of non-contiguous frames that need to get rendered or if you're trying to simulate something like timelapse photography or have unusual requirements for which frames need to be rendered.

The framelist text file should contain one line of text with each frame number separated by a comma and no spaces. Here is an example:

```
455427,456321,457215,458109,459004,459898,460792,461686,462580,463474,464369,465263
```

Additional Notes
----------------

* It is assumed that you have already installed and successfully run the original win_brenda_console application before trying this fork. In order to run this modified version of win_brenda_console, you must add these lines to your .brenda.conf file before running this for the first time, otherwise you will encounter an error:

```
AVAILABILITY_ZONE=us_east-1c
FRAME_LIST_FILE=
FRAME_LIST_OR_FRAME_RANGE=FRAME_RANGE
BLENDER_DIR_IN_ZIP_FILE=

```


Good Workflow Structure
-----------------------

The idea for a "good workflow" directory structure came from Kenny Roy's "Proper Project Setup for Animation" lecture: https://www.youtube.com/watch?v=5bIbWbDZWs8 This lecture uses Maya; the basic ideas presented in the lecture have been modified to work with Blender.

Most directories are broken down into _sequences_ and _shots_. 

Sequences are collections of shots. Sequences are identified by three uppercase letters (e.g. SEQ, NYC, PAR -- whatever three letters describe what's going on in the scene).

Shots are identified by three numbers (e.g. 010, 020, 052, 123, 523), except in the case of `ALL` (explained shortly). 

When creating shots, it's recommended to start at 010 and increment them by 10. That way, if it turns out that you need a new shot in between two other shots, you have a total of nine other numbers you could use in between shots, and you won't need to restructure a lot of your project.

`ALL` is a reserved sequence name. When Better Brenda sees a sequence directory called `ALL`, it _always_ pulls in everything in that directory into the zip file that gets uploaded to AWS. You may also use `ALL` as a shot name. Just like when you use `ALL` as a sequence name, using `ALL` as a shot name will be sent to AWS if it's part of a sequence that is also sent to AWS.

`not in project` is a reserved directory name. If you create a directory anywhere in your "good workflow" project structure and it's in a directory that Better Brenda searches for putting together everything in a zip file, everything in the `not in project` directory will be ignored by Better Brenda. The `not in project` directories can be used to store things like reference material that should never get uploaded to AWS.

Here is the "good workflow" directory structure. Note that any directory name followed with `(*)` is a directory that Better Brenda will search through, grab the appropriate files and directories, and send to AWS.

```
P-Project: The name of the project
	|-> _IN: Anything received from the client. Every directory in here should be in the format "YYYY-MM-DD - [description of what's in the directory]".
	|
	|-> _OUT: Anything sent to the client. Every directory in here should be in the format "YYYY-MM-DD - [description of what's in the directory]".
	|
	|-> _Ref: Reference material.
	|	|-> [Sequence name]
	|		|-> [Shot number]
	|
	|-> 2D: All of the project files that are 2D based. This holds everything related to compositing.
	|	|-> Blender: Any Blender projects that are used for compositing.
	|	|	|-> [Sequence name]
	|	|		|-> [Shot number]
	|	|
	|	|-> images
	|	|	|-> boards: Storyboards.
	|	|	|
	|	|	|-> comps: Final composited images.
	|	|	|	|-> [Sequence name]
	|	|	|		|-> [Shot number]
	|	|	|
	|	|	|-> mattes (*): Any mattes used in compositing.
	|	|	|	|-> [Sequence name]
	|	|	|		|-> [Shot number]
	|	|	|
	|	|	|-> plates (*): Any plates used in compositing.
	|	|		|-> [Sequence name]
	|	|			|-> [Shot number]
	|	|
	|	|-> Vegas: Any Sony Vegas projects (or whatever 2D video editing suite you use)
	|		|-> [Sequence name]
	|			|-> [Shot number]
	|
	|-> 3D: All of the project files that are 3D based.
	|	|-> assets: Any sort of 3D asset.
	|	|	|-> env (*): Your finished sets (environments).
	|	|	|	|-> [Sequence name]
	|	|	|		|-> [Shot number]
	|	|	|
	|	|	|-> lighting (*): Any lighting setups used in the project.
	|	|	|	|-> [Sequence name]
	|	|	|		|-> [Shot number]
	|	|	|
	|	|	|-> models (*): Any non-rigged models used in the project.
	|	|	|	|-> [Sequence name]
	|	|	|		|-> [Shot number]
	|	|	|
	|	|	|-> rigs (*): Any rigged models used in the project.
	|	|	|	|-> [Sequence name]
	|	|	|		|-> [Shot number]
	|	|	|
	|	|	|-> worlds (*): Any worlds (skies) used in the project.
	|	|		|-> [Sequence name]
	|	|			|-> [Shot number]
	|	|	
	|	|-> audio: Audio that's used as a reference in the Blender projects; this is NOT used in your final video edit.
	|	|	|-> [Sequence name]
	|	|		|-> [Shot number]
	|	|
	|	|-> data (*): Particle simulation files as well as anything that a Blender file needs that doesn't fit into another directory.
	|	|	|-> [Sequence name]
	|	|		|-> [Shot number]
	|	|
	|	|-> fonts (*): Fonts that are used in a Blender scene file.
	|	|	|-> [Sequence name]
	|	|		|-> [Shot number]
	|	|
	|	|-> images (*): Images that are used in a Blender scene file.
	|	|	|-> [Sequence name]
	|	|		|-> [Shot number]
	|	|
	|	|-> imageseqs (*): Image sequences that are used in a Blender scene file.
	|	|	|-> [Sequence name]
	|	|		|-> [Shot number]
	|	|
	|	|-> renders: Blender renders. These files are brought into compositing.
	|	|	|-> [Sequence name]
	|	|		|-> [Shot number]
	|	|
	|	|-> scenes: Master Blender files that contain entire shots.
	|	|	|-> [Sequence name]
	|	|		|-> [Shot number]
	|	|
	|	|-> zzExperiments: Test projects that are created for the sake of research and development. Nothing in here gets used in the real production.
	|	
	|-> audio: The audio that will be used in the final video edit.
	|	|-> music
	|	|	|-> [Sequence name]
	|	|		|-> [Shot number]
	|	|
	|	|-> sfx: Sound effects
	|	|	|-> [Sequence name]
	|	|		|-> [Shot number]
	|
	|-> docs: Any documentation (spreadsheets, production diaries, credits, behind-the-scenes pictures) related to the project.
	|
	|-> editorial: All of the finished, rendered video files. 

```

It is assumed that, when you select the .blend file to upload as part of a "good workflow" directory structure, the file is located in one of these directories:

```
"P-Project\2D\Blender\[Sequence name]\[Shot number]\"
"P-Project\3D\scenes\[Sequence name]\[Shot number]\"
```

When you upload the .blend file from one of these directories, Better Brenda will not upload anything else from the directory; it will upload _only_ the .blend file you have selected. As mentioned previously, Better Brenda will also search through all of the directories marked with `(*)` above.

To work with an actual example of the "good workflow" directory structure, copy the _support/P-Project_ directory to somewhere outside of your local repository and remove all of the files called _.gitkeep_. You can use this demo structure to upload a working Blender project via Better Brenda. The included demo .blend file, `P-Project\3D\scenes\SEQ\010\SEQ_010_v001.blend`, links to other objects in the folder structure. 