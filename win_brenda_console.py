import time
import os
from decimal import *
import shutil
from Tkinter import *
from tkFileDialog import *
import ConfigParser
from ConfigParser import SafeConfigParser
import urlparse
import zipfile
import urllib2
import urllib
import sys
from time import sleep
from datetime import datetime

def spacetime ():
    time.sleep(3)
    clear()

def menerror():
    clear()
    print "Please choose an option from the menu..."
    time.sleep(2)
    clear()
 
clear = lambda: os.system('cls')

DIR_BRENDA_CODE = 'c:/brenda-master'
DIR_PYTHON27_SCRIPTS = 'c:/Python27/Scripts'
DIR_APPDATA_ROAMING = '/AppData/Roaming/'
FILE_INI_FILE = 's3cmd.ini'
EXTENSION_S3CFG = '.s3cfg'
ZONE_BASE = 'us-east-1' # TODO: This should be pulled from a config file or from a Brenda command response so it's not tied to a particular region
NOT_IN_PROJECT = "NOT IN PROJECT"
start_time = datetime(1900,1,1)

sys.path.insert(0, DIR_BRENDA_CODE+'/brenda')
import ami


os.chdir(DIR_BRENDA_CODE)




def mainmenuoptions ():
    print
    print
    print
    print
    print " s = Setting up your farm"
    print " m = Managing your farm"
    print " d = Download rendered frames"
    print " c = Canceling and resetting your farm"
    print
    print

def mainmenu ():
    while True:
        clear()
        mainmenuoptions ()
        submen = raw_input(' Which task would you like to perform? ')
        if submen =='s':           
            setupmenu()    
        if submen =='m':           
            monmenu()
        if submen =='d':
            downmenu()   
        if submen =='c':           
            cancelmenu()

             

def setupmenuoptions ():
    print 
    print " m = Go to previous menu"
    print
    print
    print " a = AMI"
    print " p = Project"
    print " f = Frames"
    print " i = Instances"
    print " r = Review details with option to start job"
    print
    print


def amis ():
    clear()
    reload(ami)

    while True:
        clear()
        print
        print ' m = Go to previous menu'
        print
        print
        print ' a = Input your own AMI'
        print
        print ' (Current AMI = '+ami.AMI_ID+')'
        print
        print
        amiconf = raw_input(' Which task would you like to perform? ')
        if amiconf =='m':
            clear()
            break
        elif amiconf =='a':
            clear()
            print
            ami_user = raw_input(' Enter the new public AMI you wish to use: ')
            clear()
            print
            print ' Your new AMI will be changed to "'+ami_user+'"'
            print
            print
            amiconf = raw_input(' Do you want to continue? (y/n) ')
            if amiconf=='y':
                clear()
                os.chdir(DIR_BRENDA_CODE+'/brenda')
                file = open("ami.py", "w")
                w = """# An AMI that contains Blender and Brenda (may be None)
AMI_ID="""
                file.write(w+'"'+ami_user+'"')
                file.close()
                print
                print " Changed AMI to "+ami_user
                spacetime()
                os.chdir(DIR_BRENDA_CODE)
                break
            if amiconf=='n':
                clear()
                break

def nproj():
    clear()
    print
    print " Select your Blender project file (texture files etc. must be packed)..."
    time.sleep(1)
    root = Tk()
    root.withdraw()
    projfile = askopenfilename(parent=root, title='Select your packed Blender project file')
    root.destroy()
    projfilename = os.path.basename(os.path.abspath(projfile))
    projfilepath = os.path.dirname(os.path.abspath(projfile))
    uploadproject(projfilename, projfilepath, 0)

def nprojexternal():
    clear()
    print
    print ' Select your Blender project file. External artwork files must be the directory "/artwork/in project/" and your project must use relative file paths.'
    time.sleep(1)
    root = Tk()
    root.withdraw()
    projfile = askopenfilename(parent=root, title='Select your Blender project file')
    root.destroy()
    projfilename = os.path.basename(os.path.abspath(projfile))
    projfilepath = os.path.dirname(os.path.abspath(projfile))
    uploadproject(projfilename, projfilepath, 1)

def nprojworkflow():
    clear()
    print
    print 'Select your Blender project file.\n'
    print 'Your project must meet the following criteria:\n'
    print ' * Have a filename with a 3-character scene followed by an underscore followed by a 3-character shot number.'
    print '   (e.g. "SEQ_010.blend", "SEQ_020_v002.blend", "PAR_001_anything_goes_here.blend")\n'
    print ' * Use relative file paths.\n'
    print ' * Have a project folder structure as outlined in the "good workflow" document.\n'
    print ' * The project file must be located inside this directory:'
    print '   [project directory]/3D/scenes/[3 character scene]/[3 character shot number]/'
    time.sleep(1)
    root = Tk()
    root.withdraw()
    projfile = askopenfilename(parent=root, title='Select your Blender project file')
    root.destroy()
    projfilename = os.path.basename(os.path.abspath(projfile))
    projfilepath = os.path.dirname(os.path.abspath(projfile))
    uploadproject(projfilename, projfilepath, 3)

def nprojzipped():
    clear()
    print
    print ' Select your zipped archive. Your zipped archive must have the same name as your main .blend file and your project must use relative file paths.'
    time.sleep(1)
    root = Tk()
    root.withdraw()
    projfile = askopenfilename(parent=root, title='Select your zipped archive')
    root.destroy()
    projfilename = os.path.basename(os.path.abspath(projfile))
    projfilepath = os.path.dirname(os.path.abspath(projfile))
    uploadproject(projfilename, projfilepath, 2)

def get_subdirectories(absolute_project_directory, relative_subdirectory, is_sequence_directory = False):
    # Returns a list of local subdirectories where we need to non-recursively zip up all of the files.
    # We ignore any directories called "not in project".
    # relative_subdirectory should not start with a backslash.
    # If is_sequence_directory = True then we will not pull in ANY 3-numbered directories, but we'll pull in all of
    # the other directories.
    print 'get_subdirectories() called!!!!!!!!!!!!!!!!!!!!!!!!!'
    print '     absolute_project_directory: ' + absolute_project_directory
    print '          relative_subdirectory: ' + relative_subdirectory
    retval = []
    retval.append(relative_subdirectory) # We need to append the actual directory because otherwise it's never added to the list.

    source_dir = os.path.abspath(os.path.join(absolute_project_directory, relative_subdirectory))
    print '                     source_dir: ' + source_dir
    for root, dirs, files in os.walk(source_dir):
        # add directory (needed for empty dirs)
        for dir in dirs:
            # Get a stripped down version of the entire path for testing. All we care about is whether
            # NOT_IN_PROJECT is in the string from the absolute_project_directory onwards; it is legal
            # to have a path like c:\not in project\P-Project\3D\assets\env etc.
            # It is also legal to have a path like c:\P-Project\3D\assets\not in project but it really is\stuff
            full_path = os.path.join(root, dir)
            relative_path = full_path[len(source_dir):]
            print '                           full_path: ' + full_path
            print '                       relative_path: ' + relative_path
            if (dir.strip().upper() != NOT_IN_PROJECT and '\\' + NOT_IN_PROJECT + '\\' not in relative_path.upper()):
                # OK, at least we know that NOT_IN_PROJECT isn't here. Let's also check for 3-numbered directories, if needed.
                # Note that there is a special case that we need to prepare for -- if we're in a sequence directory and there's
                # a number directory under that (which we don't want to pick up), but under that number directory there's a
                # non-number directory -- for dir in dirs will pick up ALL of those directories, so we need to prevent that.
                beginning_of_relative_path = relative_path.split('\\')[1]
                print '          beginning_of_relative_path: ' + beginning_of_relative_path
                if (is_sequence_directory == False) or \
                        not (is_sequence_directory == True and len(beginning_of_relative_path) == 3 and beginning_of_relative_path.isdigit() == True):
                    print '            appending this: ' + os.path.join(relative_subdirectory, relative_path[1:])
                    retval.append(os.path.join(relative_subdirectory, relative_path[1:])) # We need to strip the leading backslash from relative_path, otherwise os.path.join won't work
    return retval

def uploadproject(projfilename, projfilepath, uploadtype):
    # uploadtype = 0: Uploading just a project file
    #            = 1: Uploading a project file and we will include everything in the "/artwork/in project" directory
    #            = 2: Uploading an already zipped archive
    #            = 3: Uploading a project file with "good workflow" folder structure plus external artwork files
    while True:
        clear()
        print
        print ' ***WARNING***'
        print
        print
        print ' This will...'
        print
        print
        print ' 1. Delete all of the files in your frame and project buckets.'
        print
        if (uploadtype == 1):
            print ' 2. Upload ' + projfilename + ' as well as any files in the "artwork/in project" directory.'
        elif (uploadtype == 2):
            print ' 2. Upload the already-zipped archive ' + projfilename
        elif (uploadtype == 3):
            print ' 2. Upload the project file ' + projfilename + ' as well as any external files determined by the "good workflow"'
            print '    folder structure.'
        else:
            print ' 2. Upload ' + projfilename
        print
        print ' 3. Reset the work queue.'
        print
        print
        nprojconf = raw_input(' Do you want to continue? (y/n) ')
        if nprojconf=='y':
            clear()

            #gets various variables
            from os.path import expanduser
            home = expanduser("~")
            os.chdir(home)
            parser = ConfigParser.ConfigParser()
            parser.readfp(FakeSecHead(open('.brenda.conf')))
            #find original values
            b = parser.get('asection', 'BLENDER_PROJECT')
            d = parser.get('asection', 'RENDER_OUTPUT')

            projbucketname = urlparse.urlsplit(b).netloc
            projbucketpath = 's3://'+projbucketname
            print
            print "projbucketpath: " + projbucketpath

            #changes to s3cmd working directory
            print
            print "Changing to s3cmd working directory: " + DIR_PYTHON27_SCRIPTS
            os.chdir(DIR_PYTHON27_SCRIPTS)


            #deletes all old project files
            print
            print "Deleting all project files"
            print 'python s3cmd del -r -f '+projbucketpath
            status = os.system('python s3cmd del -r -f '+projbucketpath)

            #deletes all old frames
            print
            print "Deleting all old frames"
            print 'python s3cmd del -r -f '+d
            status = os.system('python s3cmd del -r -f '+d)
            print
            print " Files in project and frame buckets have been deleted"

            #zips and moves selected file to s3 bucket
            print
            if (uploadtype == 2):
                print " Uploading project file..."
            else:
                print " Zipping and uploading project file..."
            print
            print " This may take a while"
            print
            print "Changing to this directory: " + projfilepath
            os.chdir(projfilepath)
            zipper = '.zip'
            projfilenamestripped = os.path.splitext(projfilename)[0]
            zippedprojfilename = projfilenamestripped+zipper

            if (uploadtype == 0):
                output = zipfile.ZipFile(zippedprojfilename, 'w')
                output.write(projfilename)
                output.close()
                conf_set_param('BLENDER_DIR_IN_ZIP_FILE', '')
                print zippedprojfilename + " has been created"
                print
            elif (uploadtype == 1):
                # Grab everything in the relative "artwork/in project" directory and zip it up.
                source_dir = projfilepath + "\\artwork\\in project\\"
                relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
                with zipfile.ZipFile(zippedprojfilename, "w", zipfile.ZIP_DEFLATED) as output:
                    output.write(projfilename)
                    for root, dirs, files in os.walk(source_dir):
                        # add directory (needed for empty dirs)
                        output.write(root, "artwork\\" + os.path.relpath(root, relroot))
                        for file in files:
                            filename = os.path.join(root, file)
                            if os.path.isfile(filename): # regular files only
                                arcname = os.path.join("artwork\\" + os.path.relpath(root, relroot), file)
                                output.write(filename, arcname)
                conf_set_param('BLENDER_DIR_IN_ZIP_FILE', '')
                print zippedprojfilename + " has been created"
                print
            elif (uploadtype == 2):
                # The file is already zipped.
                conf_set_param('BLENDER_DIR_IN_ZIP_FILE', '')
            elif (uploadtype == 3): # GOOD_WORKFLOW_ZIP.
                # Here's how GOOD_WORKFLOW_ZIP works:
                #   * "ALL" is a reserved sequence name. We pull in everything from an "ALL" sequence directory.
                #   * We assume the initial blend file was in "P-Project\3D\scenes\SEQ\010\" and will
                #     grab the Blender file ONLY from this directory. If there is anything else in this directory
                #    (artwork directory, other files), we just ignore it.
                #   * We assume the two directories prior to the Blender file represent the sequence and shot
                #     directories, and we will look for things with the same sequence and shot directories.
                #   * When we look in a sequence directory, we ignore any directories that have a three number value
                #     (we don't want to pull in any other shots) but we DO pull in all of the other directories (except
                #     for any directory that says "not in project"). We pull in all files in a sequence directory.
                #   * We look in the following directories and recursively pull in EVERYTHING in them, but we do not
                #     pull in any directory called "not in project".
                #       - P-Project\3D\assets\env\ALL\
                #       - P-Project\3D\assets\env\SEQ\
                #       - P-Project\3D\assets\env\SEQ\010\
                #       - P-Project\3D\assets\models\ALL\
                #       - P-Project\3D\assets\models\SEQ\
                #       - P-Project\3D\assets\models\SEQ\010\
                #       - P-Project\3D\assets\rigs\ALL\
                #       - P-Project\3D\assets\rigs\SEQ\
                #       - P-Project\3D\assets\rigs\SEQ\010\
                #       - P-Project\3D\assets\worlds\ALL\
                #       - P-Project\3D\assets\worlds\SEQ\
                #       - P-Project\3D\assets\worlds\SEQ\010\

                # Let's determine the sequence and shot number, based on the directory structure.
                path_list = projfilepath.split(os.sep)
                if (len(path_list) < 2):
                    print "There was an error parsing the project file path."
                    break
                sequence_name = path_list[-2]
                shot_number = path_list[-1]
                print 'Sequence name: ' + sequence_name
                print '       Shot #: ' + shot_number

                # Let's figure out the root of the project. The typical projfilepath path would be like this...
                #   D:\video\P-Project\3D\scenes\SEQ\010\
                # ...and we'd want to grab this as the root:
                #   D:\video\P-Project\
                # So we need to take the root and go up four directories.
                abs_project_path = os.path.abspath(os.path.join(projfilepath + '\\..\\..\\..', os.pardir))
                directories_to_zip = []
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\assets\\env\\ALL\\')
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\assets\\env\\' + sequence_name, True)
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\assets\\env\\' + sequence_name + '\\' + shot_number)
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\assets\\models\\ALL\\')
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\assets\\models\\' + sequence_name, True)
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\assets\\models\\' + sequence_name + '\\' + shot_number)
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\assets\\rigs\\ALL\\')
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\assets\\rigs\\' + sequence_name, True)
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\assets\\rigs\\' + sequence_name + '\\' + shot_number)
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\assets\\worlds\\ALL\\')
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\assets\\worlds\\' + sequence_name, True)
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\assets\\worlds\\' + sequence_name + '\\' + shot_number)
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\data\\ALL\\')
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\data\\' + sequence_name, True)
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\data\\' + sequence_name + '\\' + shot_number)
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\images\\ALL\\')
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\images\\' + sequence_name, True)
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\images\\' + sequence_name + '\\' + shot_number)
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\imageseqs\\ALL\\')
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\imageseqs\\' + sequence_name, True)
                directories_to_zip += get_subdirectories(abs_project_path, '3D\\imageseqs\\' + sequence_name + '\\' + shot_number)

                print '+++++++++++++++++++++++++++++++++++++++++++++++++++'
                print 'DIRECTORIES TO ZIP: '
                print
                for d in directories_to_zip:
                    print '    ' +d
                print '+++++++++++++++++++++++++++++++++++++++++++++++++++'


                print 'Zipping up project "' + zippedprojfilename + '"...'

                with zipfile.ZipFile(zippedprojfilename, "w", zipfile.ZIP_DEFLATED) as output:
                    for relative_dir in directories_to_zip:
                        # Figure out where the files are on the local hard drive for this dir so we know were to grab things
                        source_dir = os.path.abspath(os.path.join(abs_project_path, relative_dir))
                        relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
                        print 'source_dir: ' + source_dir # TODO: REMOVE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        print '   relroot: ' + relroot # TODO: REMOVE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        print '  Zipping files from "' + source_dir + '"...'
                        for root, dirs, files in os.walk(source_dir):
                            for file in files:
                                filename = os.path.join(root, file)
                                print 'filename: ' + filename # TODO: REMOVE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                                if os.path.isfile(filename):  # regular files only
                                    print '    Adding "' + filename + '"...'
                                    #arcname = os.path.join(relative_dir + '\\' + os.path.relpath(root, relroot), file)
                                    arcname = os.path.join(relative_dir, os.path.relpath(root, relroot))
                                    print '    **** relative_dir: ' + relative_dir
                                    print '    ****         root: ' + root
                                    print '    ****      relroot: ' + relroot
                                    print '    ****         file: ' + file
                                    print '    ****      arcname: ' + arcname
                                    print '    **** writing this: ' + relative_dir + '\\' + file
                                    output.write(filename, relative_dir + '\\' + file)
                            break  # Prevent descending into subfolders. This works because os.walk first lists the files in the requested folder and then goes into subfolders.
                    # Lastly, write the actual .blend project file in its proper directory.
                    relative_project_path = projfilepath[len(abs_project_path):] # This is also the path that frame-template and subframe-template need to start from when finding the blend file.
                    print '--------          projfilepath: ' + projfilepath
                    print '--------          projfilename: ' + projfilename
                    print '--------      abs_project_path: ' + abs_project_path
                    print '-------- len(abs_project_path): ' + str(len(abs_project_path))
                    print '-------- relative_project_path: ' + relative_project_path
                    output.write(projfilename, relative_project_path + '\\' + projfilename)
                    conf_set_param('BLENDER_DIR_IN_ZIP_FILE', relative_project_path)
                print zippedprojfilename + " has been created"
                print

            print
            exit = raw_input(' LOOK AT YOUR ZIP FILE Press Enter to continue ') # TODO: REMOVE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            print "Changing to s3cmd working directory: " + DIR_PYTHON27_SCRIPTS
            os.chdir(DIR_PYTHON27_SCRIPTS)
            print
            print 'python s3cmd put --no-mime-magic --multipart-chunk-size-mb=5 "'+projfilepath+'/'+zippedprojfilename+'" '+projbucketpath
            os.system('python s3cmd put --no-mime-magic --multipart-chunk-size-mb=5 "'+projfilepath+'/'+zippedprojfilename+'" '+projbucketpath)
            print
            print ' Project file has been uploaded'

            #deletes zipped file from users pc
            if (uploadtype != 2):
                print
                print "Deleting zipped file from user's PC"
                os.chdir(projfilepath)
                os.remove(zippedprojfilename)

            conf_set_param('BLENDER_PROJECT', projbucketpath+'/'+zippedprojfilename)

            resetworkqueue()
            exit = raw_input(' Press Enter to continue ')
	    clear()
            break
        if nprojconf=='n':
            clear()
            break

def workq():
    while True:
        clear()
        print
        sframe = raw_input(' Animation start frame? ')
        clear()
        print
        eframe = raw_input(' Animation end frame? ')       
        clear()
        totalFrames = 1+int(eframe)-int(sframe)
        print
        print " Your animation starts at frame "+sframe,"and ends at frame "+eframe+"." 
        print
        if totalFrames==1:
            print " One frame will be rendered."
        else:
            print " A total of "+str(totalFrames)+" frames will be rendered."
        print
        qconf = raw_input(' Are these values correct? (y/n) ')
        if qconf=='y':
            clear()
            conf_set_param('START_FRAME', sframe)
            conf_set_param('END_FRAME', eframe)
            conf_set_param('FRAME_LIST_OR_FRAME_RANGE', 'FRAME_RANGE')
            print
            print ' Frame range changed (' + sframe + '-' + eframe + ')'
            spacetime()
            break
        if qconf=='n':
            clear()
            print
            print ' Frame range not changed'
            spacetime()
            break

def framelist():
    clear()
    print
    print "Select your framelist text file."
    print
    print "The framelist text file should contain one line of text with each frame number separated by a comma and no spaces."
    print
    print "Example:"
    print "455427,456321,457215,458109,459004,459898,460792,461686,462580,463474,464369,465263"
    time.sleep(1)
    root = Tk()
    root.withdraw()
    framelistfile = askopenfilename(parent=root, title='Select your framelist text file')
    root.destroy()

    conf_set_param('FRAME_LIST_OR_FRAME_RANGE', 'FRAME_LIST')
    conf_set_param('FRAME_LIST_FILE', framelistfile)

    clear()
    print "Going to use this file as the frame list:"
    print framelistfile
    print
    with open(framelistfile) as f:
        totalframes = len(f.readline().strip().split(','))
    print "This file has a total of " + str(totalframes) + " frame(s)."
    print
    exit = raw_input(' Press Enter to continue ')

def prices():
    clear()
    printspotrequest('c3.large')
    printspotrequest('c3.xlarge')
    printspotrequest('c3.2xlarge')
    printspotrequest('c3.4xlarge')
    printspotrequest('c5.large')
    printspotrequest('c5.xlarge')
    printspotrequest('c5.2xlarge')
    printspotrequest('c5.4xlarge')
    exit = raw_input(' Press Enter to continue ')

def reviewjob():
    while True:
        clear()
        conf = read_conf_values()
        b = conf.b
        projbucketname = urlparse.urlsplit(conf.b).netloc
        projname = b.split('/')[-1]
        projname = os.path.splitext(projname)[0]
        framebucket = urlparse.urlsplit(conf.d).netloc
        reload(ami)
        intstartframe = int(conf.k)
        intendframe = int(conf.l)
        if conf.o == 'FRAME_RANGE':
            totalframe = intendframe-intstartframe+1
        else: # FRAME_LIST
            # Look at what we have in our frame list so we can see how many frames there are
            # as well as provide some example frame numbers.
            with open(conf.n) as f:
                framelist = f.readline().strip().split(',')
                totalframe = len(framelist)
                indx=0
                textFrameList = ''
                for frame in framelist:
                    if indx > 0:
                        textFrameList = textFrameList + ', '
                    textFrameList = textFrameList + frame
                    indx=indx+1
                    if indx>4:
                        textFrameList = textFrameList + '...'
                        break
                textFrameList = '[' + textFrameList + ']'

        if conf.j =='specifiedinfile':
            conf.j = 'as specified in uploaded .blend file'
        cost = Decimal(conf.i)
        number = Decimal(conf.h)
        math = cost*number
        totalNumberOfFiles = totalframe
        if conf.f == 'subframe':
            totalNumberOfFiles = totalframe * int(conf.g) * int(conf.g)
        print "\n"
        print " %-25s %-15s" % ('AMI used',ami.AMI_ID)
        print " %-25s %-15s" % ('Project name',projname)
        print " %-25s %-15s" % ('Frame or sub-frame',conf.f)
        if conf.f == 'subframe':
            x = 'x'
            print " %-25s %-15s" % ('Tile grid',conf.g+x+conf.g)
        print " %-25s %-15s" % ('Frame format',conf.j)
        print " %-25s %-15s" % ('Instance type',conf.a)
        print " %-25s %-15s" % ('Availability zone',conf.m)
        print "\n"
        if conf.o == 'FRAME_RANGE':
            print " Using Frame Range:"
            print " %-25s %-15s" % ('  Start frame',conf.k)
            print " %-25s %-15s" % ('  End frame',conf.l)
            print " %-25s %-15s" % ('  Total frames',totalframe)
        else: # FRAME_LIST
            print " Using Frame List:"
            print " %-25s %-15s" % ('  Example frames',textFrameList)
            print " %-25s %-15s" % ('  Total frames',totalframe)
        print "\n"
        print " %-25s %-15s" % ('Number of instances',conf.h)
        print " %-25s %-15s" % ('Bid per instance',conf.i)
        print " %-25s %-15s" % ('Cost per hour',math)
        print "\n"
        print " %-25s %-15s" % ('Total number of files (if 2D or if combining 3D L&R images to one file)',totalNumberOfFiles)
        print " %-25s %-15s" % ('Total number of files (if 3D and separate L&R images)',totalNumberOfFiles * 2)
        print "\n\n"
        rconf = raw_input(' Would you like to start the job? (y/n) ')
        if rconf == 'n':
            clear()
            print
            print ' Job not started'
            spacetime()
            break
        if rconf =='y':
            clear()
            print
            print ' This will build the work queue and initiate instances.'
            print
            doublerconf = raw_input(' Are you sure? (y/n) ')

            if doublerconf =='n':
                clear()
                print
                print ' Job not started'
                spacetime()
                break

            if doublerconf == 'y':
                clear()
                print 'Updating frame template files...'
                updateframetemplateformat()
                print 'Done updating frame template files.'
                exit = raw_input(' CHECK YOUR FRAME TEMPLATE FILE!!!!!!!!!! Press Enter to continue ') # TODO: REMOVE!!!!!!!!!!!!!!!!!!!!!!!

                os.chdir(DIR_BRENDA_CODE)
                if conf.f == 'frame':
                    if conf.o == 'FRAME_RANGE': # We have a normal range of frames, so we need to put a "push" at the end of this call
                        queue = 'python brenda-work -T frame-template -s '+conf.k+' -e '+conf.l+' push'
                    else: # FRAME_LIST
                        queue = 'python brenda-work -T frame-template -f "'+conf.n+'" push_with_frame_script'
                if conf.f == 'subframe':
                    if conf.o == 'FRAME_RANGE': # We have a normal range of frames, so we need to put a "push" at the end of this call
                        queue = 'python brenda-work -T subframe-template -s '+conf.k+' -e '+conf.l+' -X '+conf.g+' -Y '+conf.g+' push'
                    else: # FRAME_LIST
                        queue = 'python brenda-work -T subframe-template -f "'+conf.n+'" -X '+conf.g+' -Y '+conf.g+' push_with_frame_script'

                status = os.system(queue)
                print '\n'

                if status == 1:
                    print ' There was an error building work queue'
                    exit = raw_input(' Press Enter to continue ')
                    break

                if status == 0:
                    print ' Work queue has been built'
                    print
                    instrequest = 'python brenda-run -i '+conf.a+' -N '+conf.h+' -p '+conf.i+' spot -z '+conf.m
                    print instrequest
                    print '\n'
                    status = os.system(instrequest)
                    print
                    print
                    if status == 1:
                        print '\n'
                        print ' There was an error initiating instances. Try a C3 instance type for this AMI'
                        resetworkqueue()
                        exit = raw_input(' Press Enter to continue ')
                        break
                    if status == 0:
                        print '\n'
                        print ' Instance/s have been initiated.'
                        print
                        print
                        timer(1)
                        break

def instance():
    while True:
        clear()
        print
        print " a = c3.large"
        print " b = c3.xlarge"
        print " c = c3.2xlarge"
        print " d = c3.4xlarge"
        print " e = c5.large"
        print " f = c5.xlarge"
        print " g = c5.2xlarge"
        print " h = c5.4xlarge"
        print
        inst = raw_input(' Which instance would you like to use? ')

        clear()
        global type
        while True:
            if inst == 'a':
                instype = 'c3.large'
                break
            if inst == 'b':
                instype = 'c3.xlarge'
                break
            if inst == 'c':
                instype = 'c3.2xlarge'
                break
            if inst == 'd':
                instype = 'c3.4xlarge'
                break
            if inst == 'e':
                instype = 'c5.large'
                break
            if inst == 'f':
                instype = 'c5.xlarge'
                break
            if inst == 'g':
                instype = 'c5.2xlarge'
                break
            if inst == 'h':
                instype = 'c5.4xlarge'
                break
        print
        printspotrequest(instype)
        print
        print " a = " + ZONE_BASE + "a"
        print " b = " + ZONE_BASE + "b"
        print " c = " + ZONE_BASE + "c"
        print " d = " + ZONE_BASE + "d"
        print " e = " + ZONE_BASE + "e"
        print " f = " + ZONE_BASE + "f"
        print
        zone = raw_input(' Which availability zone would you like to use? ')
        print
        price = raw_input(' How much would you like to bid per instance hour (#.##)? ')

        clear()
        conf = read_conf_values()

        if conf.o == 'FRAME_RANGE':
            totalFrames = 1 + int(conf.l) - int(conf.k)
        else: # FRAME_LIST
            with open(conf.n) as f:
                totalFrames = len(f.readline().strip().split(','))

	if totalFrames==1:
            print " You have selected only one frame to render."
        else:
            print " You have selected a total of "+str(totalFrames)+" frames to render."
        print

	if conf.f=='subframe':
            totalNumOfInstances = totalFrames * int(conf.g) * int(conf.g)
	    amtPerHour = totalNumOfInstances * float(price)
	    print " You have selected subframe rendering ("+conf.g+"x"+conf.g+")."
            print 
            print " For the fastest possible rendering time, use a total of "+str(totalNumOfInstances)+" instances ($"+price+" per instance, $"+str(amtPerHour)+" an hour)."
        else:
            totalNumOfInstances = totalFrames
	    amtPerHour = totalNumOfInstances * float(price)
            print " You have selected whole frame rendering."
            print 
            print " For the fastest possible rendering time, use a total of "+str(totalNumOfInstances)+" instances ($"+price+" per instance, $"+str(amtPerHour)+" an hour)."
	print 
	print 
        amount = raw_input(' How many instances would you like to initiate? ')

        clear()
        zonetype = ZONE_BASE + zone
        print
        print " You are bidding for " + amount + " x " + instype + " in availability zone " + zonetype + " at a cost of $" + price + " per instance."
        print
        amountD = Decimal(amount)
        priceD = Decimal(price)
        math = (amountD*priceD)
        print ' This will cost you $'+ str(math), 'per hour'
        print
        print
        iconf = raw_input(' Are these values correct? (y/n) ')
        if iconf=='y':
            clear()

            conf_set_param('NUMBER_INSTANCES', amount)
            conf_set_param('INSTANCE_TYPE', instype)
            conf_set_param('PRICE_BID', price)
            conf_set_param('AVAILABILITY_ZONE', zonetype)

            print
            print ' Instance information has been changed to'
            print
            print ' ' + amount + ' x ' + instype + ' using availability zone ' + zonetype +' instances @ $' + price +' each per hour'
            spacetime()
            break

        if iconf =='n':
            clear()
            print
            print ' Instance information not changed'
            spacetime()
            break


        
def setupmenu ():
    while True:
        clear()
        status = os.chdir(DIR_BRENDA_CODE)
        setupmenuoptions()
        setuptask = raw_input(' Which task would you like to perform? ')    
        if setuptask=='m':
            clear()
            break
        if setuptask=='a':  
            clear()
            amis()
        if setuptask=='p':
            clear()
            projectmenu()
        if setuptask=='f':
            clear()
            frames()
        if setuptask=='i':  
            clear()
            instancemenu()
        if setuptask=='r':
            clear()
            reviewjob()


def monmenuoptions ():
    print 
    print " m = Go to previous menu"
    print
    print
    print " w = Work queue status"
    print " r = Run status"
    print " u = Uptime of instances"
    print " f = Farm performance"
    print " c = Instance task (frame) count"
    print " p = Prune instances"
    print " l = Tail log from instances"
    print " t = See time elapsed since start of render"
    print
    print

def monmenu ():
    global start_time
    while True:
        clear()
        status = os.chdir(DIR_BRENDA_CODE)
        monmenuoptions()
        montask = raw_input(' Which task would you like to perform? ')   
        if montask=='t':           
            clear()
            if (start_time == datetime(1900,1,1)):
                start_time = datetime.now()
            timer(0)
        if montask=='m':
            clear()
            break
        if montask=='w':  
            clear()
            print
            status = os.system('python brenda-work status')
            print
            print
            exit = raw_input(' Press Enter to continue ')
        if montask=='r':  
            clear()
            print
            os.system('python brenda-run status')
            print
            print
            exit = raw_input(' Press Enter to continue ')
        if montask=='u':           
            clear()
            print
            os.system('python brenda-tool ssh uptime ')
            print
            print
            exit = raw_input(' Press Enter to continue ')
        if montask=='l':           
            clear()
            while True:
                print
                os.system('python brenda-tool ssh tail /mnt/brenda/log')
                print
                logInput = raw_input(' Enter m to go back to the previous menu, otherwise press Enter to get more of the log.')
                if logInput == 'm':
                    break
        if montask=='f':
            clear()
            print
            os.system('python brenda-tool perf')
            print  
            print
            exit = raw_input(' Press Enter to continue ')
        if montask=='c':           
            clear()
            print
            os.system('python brenda-tool ssh cat task-count')
            print
            print
            exit = raw_input(' Press Enter to continue ')
        if montask=='p':           
            clear()
            while True:
                print
                print ' Would you like to do a dry run?'
                print
                print ' y = Yes'
                print ' n = No'
                print
                dry = raw_input(' Enter your choice ')
                if dry==('y'):
                    dry = 'y'
                    break
                if dry==('n'):
                    dry = 'n'
                    break
            clear()
            while True:
                print
                print ' Would you like to only prune instances close to transitioning'
                print ' to their next billable hour?'
                print
                print ' y = Yes'
                print ' n = No'
                print
                trans = raw_input(' Enter your choice ')
                if trans=='y':
                    clear()
                    print
                    uptime = raw_input(' What should the minimum uptime (in minutes) of pruned instances be? ')
                    clear()
                    print
                    inprunet = raw_input(' How many instances would you like to reduce the farm to? ')
                    clear()
                    if dry =='y':
                        close = 'python brenda-tool -T -d -t '+uptime+' prune '+inprunet
                    if dry =='n':
                        close = 'python brenda-tool -T -t '+uptime+' prune '+inprunet
                    os.system(close)
                    print
                    exit = raw_input(' Press Enter to continue ')
                    clear()
                    break                
                if trans=='n':
                    clear()
                    print
                    inprune = raw_input(' How many instances would you like to reduce the farm to? ')
                    clear()
                    if dry =='y':
                        close2 = 'python brenda-tool -T -d prune '+inprune
                    if dry =='n':
                        close2 = 'python brenda-tool -T prune '+inprune
                    os.system(close2)
                    print
                    exit = raw_input(' Press Enter to continue ')
                    clear()
                    break

def downmenuoptions ():
    print 
    print " m = Go to previous menu"
    print
    print
    print " o = One time download to local folder"
    print " r = Regular download to local folder (to avoid a large final download)"
    print
    print

class FakeSecHead(object):
    def __init__(self, fp):
        self.fp = fp
        self.sechead = '[asection]\n'

    def readline(self):
        if self.sechead:
            try: 
                return self.sechead
            finally: 
                self.sechead = None
        else: 
            return self.fp.readline()

def downmenu ():
    while True:
        clear()
        downmenuoptions()
        downtask = raw_input(' Which task would you like to perform? ')
        if downtask =='m':
            clear()
            break
        if downtask =='o': 
            clear()
            root = Tk()
            root.withdraw()
            print
            print " Select a folder to download frames to..."
            time.sleep(1)
            dir = askdirectory(parent=root, title='Select a folder to download frames to')
            root.destroy()
            clear()
            print
            print " Downloading frames..."
            print  
            from os.path import expanduser
            home = expanduser("~")
            status = os.chdir(home)
            cp = ConfigParser.SafeConfigParser()
            cp.readfp(FakeSecHead(open('.brenda.conf')))
            RENDER_OUTPUT = cp.get('asection', 'RENDER_OUTPUT')      
            status = os.chdir(DIR_PYTHON27_SCRIPTS)
            status = os.system('python s3cmd get -r --skip-existing '+RENDER_OUTPUT+' '+dir)
            clear()
            print
            print " Frames have been downloaded"
            print
            print
            exit = raw_input(' Press Enter to continue ')
            status = os.chdir(DIR_BRENDA_CODE)
        if downtask =='r': 
            clear()
            print
            tinterval = raw_input(' Time interval between checking for new frames and downloading (minutes)? ')
            t = int(tinterval)*60
            clear()
            root = Tk()
            root.withdraw()
            print
            print " Select a folder to download frames to..."
            time.sleep(1)
            dir = askdirectory(parent=root, title='Select a folder to download frames to')
            root.destroy()
            clear()
            from os.path import expanduser
            home = expanduser("~")
            status = os.chdir(home)
            cp = ConfigParser.SafeConfigParser()
            cp.readfp(FakeSecHead(open('.brenda.conf')))
            RENDER_OUTPUT = cp.get('asection', 'RENDER_OUTPUT')
            try:
                while True:
                    print
                    print " Checking for new frames every "+tinterval,"minutes"
                    print
                    print """ Press "control-c" to stop regular download and return"""
                    print
                    status = os.chdir(DIR_PYTHON27_SCRIPTS)
                    status = os.system('python s3cmd get -r --skip-existing '+RENDER_OUTPUT+' '+dir)
                    status = os.chdir(DIR_BRENDA_CODE)
                    clear()
                    print
                    print " Checking for new frames every "+tinterval,"minutes"
                    print
                    print """ Press "control-c" to stop regular download and return"""
                    print
                    time.sleep(t)
                    clear()

            except KeyboardInterrupt:
                clear()

def cancelmenuoptions ():
    print 
    print " m = Go to previous menu"
    print
    print
    print " r = Reset work queue"
    print " s = Stop all running instances"
    print " c = Cancel pending spot requests"
    print " e = Empty frame and project buckets"
    print
    print " y = Reset work queue, stop all running instances, and cancel pending spot requests"
    print " z = Reset work queue, stop all running instances, cancel pending spot requests, and empty frame and project buckets"
    print
    print

def cancelmenu ():
    while True:
        clear()
        status = os.chdir(DIR_BRENDA_CODE)
        cancelmenuoptions()
        canceltask = raw_input(' Which task would you like to perform? ')    
        if canceltask=='m':
            clear()           
            break  

        if canceltask=='y':  
            clear()
            resetworkqueue()
            stopinstances()
            cancelpendingspots()
            exit = raw_input(' Press Enter to continue ')
            clear()

        if canceltask=='z':  
            clear()
            print
            econf = raw_input(' Would you like to (among other things) empty frame and project buckets? (y/n) ')
            if econf =='y':
                clear()
                print
                print ' This operation will (among other things) delete all files in your frame and project buckets!'
                print 
                print
                doubleeconf = raw_input(' Are you sure? (y/n) ')
                if doubleeconf == 'y':
                    clear()
                    resetworkqueue()
                    stopinstances()
                    cancelpendingspots()
                    emptybuckets()
		    exit = raw_input(' Press Enter to continue ')
                else:
                    clear()
                    print
                    print ' Frame and project buckets have not been emptied. The operation has been canceled.'
                    spacetime()
            else:
                clear()
                print
                print ' Frame and project buckets have not been emptied. The operation has been canceled.'
                spacetime()     

        if canceltask=='r':  
            clear()
            resetworkqueue()
            exit = raw_input(' Press Enter to continue ')

        if canceltask=='s':  
            clear()
            stopinstances()
            exit = raw_input(' Press Enter to continue ')
      
        if canceltask=='c':  
            clear()
            cancelpendingspots()
	    exit = raw_input(' Press Enter to continue ')

        if canceltask=='e':
            clear()
            print
            econf = raw_input(' Would you like to empty frame and project buckets? (y/n) ')
            if econf =='y':
                clear()
                print
                print ' This will delete all files in your frame and project buckets!'
                print 
                print
                doubleeconf = raw_input(' Are you sure? (y/n) ')
                if doubleeconf == 'y':
                    clear()
                    emptybuckets()
		    exit = raw_input(' Press Enter to continue ')
                else:
                    clear()
                    print
                    print ' frame and project buckets have not been emptied'
                    spacetime()
            else:
                clear()
                print
                print ' frame and project buckets have not been emptied'
                spacetime()     




#This recreates the original "s3cmd.ini" file by making a duplicate of the ".s3cmd" file created by win_brenda_installer, renaming it to "s3cmd.ini" and moving it back
def inidup ():
    from os.path import expanduser
    home = expanduser("~")
    s3cmd_there = os.path.isfile(home+DIR_APPDATA_ROAMING+FILE_INI_FILE)
    if s3cmd_there == False:
        clear()
        shutil.copyfile(home+'/'+EXTENSION_S3CFG, home+DIR_APPDATA_ROAMING+EXTENSION_S3CFG)
        os.rename(home+DIR_APPDATA_ROAMING+EXTENSION_S3CFG, home+DIR_APPDATA_ROAMING+FILE_INI_FILE)

#This changes a line in the "tool.py" file as new Ubuntu AMIs only let you ssh in as "ubuntu" and not "tool" whereas old Ubuntu AMIs let you log in as both
def toolchange():
    x = 'tool.py'
    with open(DIR_BRENDA_CODE+'/brenda/'+x, 'r') as file:
        data = file.readlines()
    data[73] = """                user = utils.get_opt(opts.user, conf, 'AWS_USER', default='ubuntu')\n"""
    with open(DIR_BRENDA_CODE+'/brenda/'+x, 'w') as file:
        file.writelines( data )

def instancemenu ():
    while True:
        clear()
        print
        print ' m = Go to previous menu'
        print
        print
        print ' p = Prices'
        print ' c = Choose instances'
        print
        print
        conf = read_conf_values()
        instchoice = raw_input(' Choose instance option: ')

        if instchoice == 'm':
            break

        if instchoice == 'p':
            prices()

        if instchoice == 'c':
            instance()

def projectmenu():
    while True:
        clear()
        print
        print ' m = Go to previous menu'
        print
        print
        print ' b = Upload .blend file'
        print ' e = Upload .blend file plus external artwork files'
        print ' w = Upload .blend file with "good workflow" folder structure plus external artwork files'
        print ' z = Upload already zipped archive'
        print
        print
        conf = read_conf_values()
        instchoice = raw_input(' Choose project option: ')

        if instchoice == 'm':
            break

        if instchoice == 'b':
            nproj()
            break

        if instchoice == 'e':
            nprojexternal()
            break

        if instchoice == 'w':
            nprojworkflow()
            break

        if instchoice == 'z':
            nprojzipped()
            break


def frames ():
    while True:
        clear()
        print
        print ' m = Go to previous menu'
        print
        print
        print ' r = Use (and set) frame range'
        print ' u = Use (and select) a frame list file (a text file containing a list of specific frames to render)'
        print ' w = Whole frames'
        print ' s = Sub-frames tiles'
        print ' f = File format'
        print
        print
        conf = read_conf_values()
        framechoice = raw_input(' Choose frame option: ')

        if framechoice == 'm':
            break

        if framechoice == 'r':
            workq()

        if framechoice == 'u':
            framelist()

        if framechoice == 'w':
            clear()

            conf_set_param('FRAME_OR_SUBFRAME', 'frame')
            conf_set_param('TILE', 'non')

            print
            print ' Changed to whole frame rendering'
            spacetime()

        if framechoice == 's':
            while True:
                x = 'x'
                clear()
                print
                print ' a = 64 8x8'
                print ' b = 16 4x4'
                print ' c = 4  2x2'
                print
                print
                tilechoice = raw_input(' How many tiles will frames be split into? ')
                clear()              
                if tilechoice =='a':
                    conf_set_param('FRAME_OR_SUBFRAME', 'subframe')
                    conf_set_param('TILE', '8')
                    print
                    print ' Changed to sub-frame rendering with 8x8 tile size'
                    spacetime()
                    break

                if tilechoice =='b':
                    conf_set_param('FRAME_OR_SUBFRAME', 'subframe')
                    conf_set_param('TILE', '4')
                    print
                    print ' Changed to sub-frame rendering with 4x4 tile size'
                    spacetime()
                    break
                if tilechoice =='c':
                    conf_set_param('FRAME_OR_SUBFRAME', 'subframe')
                    conf_set_param('TILE', '2')
                    print
                    print ' Changed to sub-frame rendering with 2x2 tile size'
                    spacetime()
                    break

        if framechoice == 'f':
            while True:
                clear()
                print
                print ' p = PNG'
                print ' e = EXR'
                print ' j = JPEG'
                print ' t = TIFF'
                print ' f = Format specified in uploaded .blend file'
                print
                print
                formatchoice = raw_input(' Enter the file format you wish frames to be rendered in? ')
                if formatchoice=='p':
                    #new values
                    clear()
                    conf_set_param('FILE_TYPE', 'PNG')
                    clear()
                    print
                    print ' Changed frame format to PNG'
                    spacetime()
                    break

                if formatchoice=='e':
                    clear()
                    conf_set_param('FILE_TYPE', 'EXR')
                    clear()
                    print
                    print ' Changed frame format to EXR'
                    spacetime()
                    break

                if formatchoice=='j':
                    clear()
                    conf_set_param('FILE_TYPE', 'JPEG')
                    print
                    print ' Changed frame format to JPEG'
                    spacetime()
                    break

                if formatchoice=='t':
                    clear()
                    conf_set_param('FILE_TYPE', 'TIFF')
                    clear()
                    print
                    print ' Changed frame format to TIFF'
                    spacetime()
                    break

                if formatchoice=='f':
                    conf_set_param('FILE_TYPE', 'specifiedinfile')
                    clear()
                    print
                    print ' Changed to format specified in uploaded .blend file'
                    spacetime()
                    break

def getfiletypeformat():
    from os.path import expanduser
    home = expanduser("~")
    os.chdir(home)
    parser = ConfigParser.ConfigParser()
    parser.readfp(FakeSecHead(open('.brenda.conf')))
    j = parser.get('asection', 'FILE_TYPE')
    retvalue = ''  # j == 'specifiedinifile'
    if j == 'PNG':
        retvalue = '-F PNG'
    elif j == 'EXR':
        retvalue = '-F EXR'
    elif j == 'JPEG':
        format_value = '-F JPEG'
    elif j == 'TIFF':
        retvalue - '-F TIFF'
    return retvalue

def getblenderdirinzipfile():
    from os.path import expanduser
    home = expanduser("~")
    os.chdir(home)
    parser = ConfigParser.ConfigParser()
    parser.readfp(FakeSecHead(open('.brenda.conf')))
    retval = parser.get('asection', 'BLENDER_DIR_IN_ZIP_FILE')
    if len(retval) > 0:
        retval = retval.replace('\\', '/') # When going through the directory structure in Linux, we need to use forward slashes
        retval = retval[1:] # Remove the initial forward slash...
        retval += '/' # ...and append a trailing slash.
        
        retval = 'scenes/SEQ/010/' # TODO: REMOVE THIS!!!!!!!!!!!!! THIS IS JUST A TEST.
    return retval

def updateframetemplateformat():
    # Updates both the regular frame template and subframe template with the current values.
    # We need to update this any time we change the output image file format or when we upload a "good workflow" project
    # structure (because we need to know where to start looking for a .blend file).
    #
    # Note that there is the flag "--enable-autoexec" on the frame and subframe template. This is the equivalent of
    # going into Blender and selecting User Preferences -> File and checking "Auto Execution: Auto Run Python Scripts".
    # If this option is not turned on and you are using BlenRig, the armature won't run correctly (FK arms and forearms
    # will stay completely straight).

    # Get our config files before we start digging around in directories.
    blender_dir_in_zip_file = getblenderdirinzipfile()
    file_type_format = getfiletypeformat()

    # Update the regular frame template.
    os.chdir(DIR_BRENDA_CODE)
    code = 'blender -b ' + blender_dir_in_zip_file + '*.blend --enable-autoexec ' + file_type_format + ' -o $OUTDIR/###### -s $START -e $END -j $STEP -t 0 -a'
    file = open("frame-template", "w")
    file.write(code)
    file.close()

    # Update the subframe template.
    code = """cat >subframe.py <<EOF
import bpy
bpy.context.scene.render.border_min_x = $SF_MIN_X
bpy.context.scene.render.border_max_x = $SF_MAX_X
bpy.context.scene.render.border_min_y = $SF_MIN_Y
bpy.context.scene.render.border_max_y = $SF_MAX_Y
bpy.context.scene.render.use_border = True
EOF
blender -b """ + blender_dir_in_zip_file + """*.blend --enable-autoexec -P subframe.py """ + file_type_format + """ -o $OUTDIR/frame_######_X-$SF_MIN_X-$SF_MAX_X-Y-$SF_MIN_Y-$SF_MAX_Y -s $START -e $END -j $STEP -t 0 -a"""
    file = open("subframe-template", "w")
    file.write(code)
    file.close()


class read_conf_values(object):
    def __init__(self):
        from os.path import expanduser
        home = expanduser("~")
        os.chdir(home)
        parser = ConfigParser.ConfigParser()
        parser.readfp(FakeSecHead(open('.brenda.conf')))
        self.a = parser.get('asection', 'INSTANCE_TYPE')
        self.b = parser.get('asection', 'BLENDER_PROJECT')
        self.c = parser.get('asection', 'WORK_QUEUE')
        self.d = parser.get('asection', 'RENDER_OUTPUT')
        self.e = parser.get('asection', 'DONE')
        self.f = parser.get('asection', 'FRAME_OR_SUBFRAME')
        self.g = parser.get('asection', 'TILE')
        self.h = parser.get('asection', 'NUMBER_INSTANCES')
        self.i = parser.get('asection', 'PRICE_BID')
        self.j = parser.get('asection', 'FILE_TYPE')
        self.k = parser.get('asection', 'START_FRAME')
        self.l = parser.get('asection', 'END_FRAME')
        self.m = parser.get('asection', 'AVAILABILITY_ZONE')
        self.n = parser.get('asection', 'FRAME_LIST_FILE')
        self.o = parser.get('asection', 'FRAME_LIST_OR_FRAME_RANGE')
        self.p = parser.get('asection', 'BLENDER_DIR_IN_ZIP_FILE')

        #create new options
        self.a_nm = 'INSTANCE_TYPE='
        self.b_nm = 'BLENDER_PROJECT='
        self.c_nm = 'WORK_QUEUE='
        self.d_nm = 'RENDER_OUTPUT='
        self.e_nm = 'DONE='
        self.f_nm = 'FRAME_OR_SUBFRAME='
        self.g_nm = 'TILE='
        self.h_nm = 'NUMBER_INSTANCES='
        self.i_nm = 'PRICE_BID='
        self.j_nm = 'FILE_TYPE='
        self.k_nm = 'START_FRAME='
        self.l_nm = 'END_FRAME='
        self.m_nm = 'AVAILABILITY_ZONE='
        self.n_nm = 'FRAME_LIST_FILE='
        self.o_nm = 'FRAME_LIST_OR_FRAME_RANGE='
        self.p_nm = 'BLENDER_DIR_IN_ZIP_FILE='
        os.chdir(DIR_BRENDA_CODE)


def confwrite(newconfig):
    from os.path import expanduser
    home = expanduser("~")
    os.chdir(home)
    file = open(".brenda.conf", "w")
    file.write(newconfig)
    file.close()
    os.chdir(DIR_BRENDA_CODE)

def compare_param_val(originalParamName, originalParamValue, desiredParamName, desiredParamValue):
    retval = originalParamName
    if (desiredParamName!=originalParamName.replace('=', '')):
        retval += originalParamValue + '\n'
    else:
        retval += desiredParamValue + '\n'
    return retval

def conf_set_param(paramName, paramValue):
    conf = read_conf_values()
    newconfig = compare_param_val(conf.a_nm, conf.a, paramName, paramValue)
    newconfig += compare_param_val(conf.b_nm, conf.b, paramName, paramValue)
    newconfig += compare_param_val(conf.c_nm, conf.c, paramName, paramValue)
    newconfig += compare_param_val(conf.d_nm, conf.d, paramName, paramValue)
    newconfig += compare_param_val(conf.e_nm, conf.e, paramName, paramValue)
    newconfig += compare_param_val(conf.f_nm, conf.f, paramName, paramValue)
    newconfig += compare_param_val(conf.g_nm, conf.g, paramName, paramValue)
    newconfig += compare_param_val(conf.h_nm, conf.h, paramName, paramValue)
    newconfig += compare_param_val(conf.i_nm, conf.i, paramName, paramValue)
    newconfig += compare_param_val(conf.j_nm, conf.j, paramName, paramValue)
    newconfig += compare_param_val(conf.k_nm, conf.k, paramName, paramValue)
    newconfig += compare_param_val(conf.l_nm, conf.l, paramName, paramValue)
    newconfig += compare_param_val(conf.m_nm, conf.m, paramName, paramValue)
    newconfig += compare_param_val(conf.n_nm, conf.n, paramName, paramValue)
    newconfig += compare_param_val(conf.o_nm, conf.o, paramName, paramValue)
    newconfig += compare_param_val(conf.p_nm, conf.p, paramName, paramValue)
    confwrite(newconfig)

def resetworkqueue():
    os.chdir(DIR_BRENDA_CODE)
    status = os.system('python brenda-work reset')
    if status==0:
        print
        print " Work queue has been reset"
        print
    if status==1:
        print
        print
        print
        print " There was a problem resetting work queue, please try waiting 60 seconds"
    os.chdir(DIR_BRENDA_CODE)

def stopinstances ():
    print
    status = os.system('python brenda-run -T stop')
    if status==0:
       print
       print
       print " Instances have been stopped"
       print
    if status==1:
       print
       print
       print
       print " There was a problem stopping the running instances. Please try an alternative method." 
       print
       print

def cancelpendingspots ():
    print
    status = os.system('python brenda-run cancel')
    if status==0:
        print
        print
        print " Pending spot requests have been cancelled"
        print
    if status==1:
        print
        print
        print
        print " There was a problem canceling the pending spot requests. Please try an alternative method."
        print
        print

def emptybuckets ():
    #gets various variables
    from os.path import expanduser
    home = expanduser("~")
    os.chdir(home)
    parser = ConfigParser.ConfigParser()
    parser.readfp(FakeSecHead(open('.brenda.conf')))
    #find original values
    b = parser.get('asection', 'BLENDER_PROJECT')
    d = parser.get('asection', 'RENDER_OUTPUT')

    projbucketname = urlparse.urlsplit(b).netloc
    projbucketpath = 's3://'+projbucketname

    #changes to s3cmd working directory
    os.chdir(DIR_PYTHON27_SCRIPTS)

    #deletes all old project files
    print
    print 'python s3cmd del -r -f '+projbucketpath
    status = os.system('python s3cmd del -r -f '+projbucketpath)

    #deletes all old frames
    print
    print 'python s3cmd del -r -f '+d
    status = os.system('python s3cmd del -r -f '+d)
    print
    print " Files in project and frame buckets have been deleted"
    print

def printspotrequest(spinstype):
    spotrequest = 'python brenda-run -i '+spinstype+' price'
    status = os.system(spotrequest)
    print

def timer(start):
    global start_time
    if (start == 1):
        start_time = datetime.now()
    print " Enter m to go back to the previous menu, otherwise press Enter to see the current elapsed render time."
    print
    while True:
        elapsed_time = datetime.now() - start_time
        hours, remainder = divmod(elapsed_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
	timerInput = raw_input('   {:02}:{:02}:{:02}  '.format(int(hours), int(minutes), int(seconds)))
	if timerInput=='m':
            break

toolchange()
inidup()
mainmenu()
