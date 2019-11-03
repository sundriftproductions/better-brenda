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

ft = 'frame-template '
sft = 'subframe-template '
strt = '-s '
end = '-e '
pu = 'push'
push_with_frame_script='push_with_frame_script'
frame_script = '-f '
sb = ' '
i = '-i '
n = '-N '
p = '-p '
zFlag = '-z '
spot = 'spot'
spotprice = 'price'

py = 'python '
bw = 'brenda-work '
br = 'brenda-run '
bt = 'brenda-tool '
sh = 'ssh '
ut = 'uptime '
st = 'status'
pf = 'perf'
tc = 'cat task-count'
tl = 'tail /mnt/brenda/log'
pru = 'prune '
smlt = '-t '
dflag = '-d '
xsize = '-X '
ysize = '-Y '

rs = 'reset'
t = '-T '
sp = 'stop'
ca = 'cancel'
bm = 'c:/brenda-master'
ps = 'c:/Python27/Scripts'
ap = '/AppData/Roaming/'
ini = 's3cmd.ini'
sl = '/'
scf = '.s3cfg'
brenda = 'brenda'
q = '"'
ff = '-F'
zonebase = 'us-east-1' # TODO: This should be pulled from a config file or from a Brenda command response so it's not tied to a particular region

start_time = datetime(1900,1,1)

sys.path.insert(0, bm+sl+brenda)
import ami


os.chdir(bm)




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
            print ' Your new AMI will be changed to '+q+ami_user+q
            print
            print
            amiconf = raw_input(' Do you want to continue, type y or n? ') 
            if amiconf=='y':
                clear()
                os.chdir(bm+sl+brenda)
                file = open("ami.py", "w")
                w = """# An AMI that contains Blender and Brenda (may be None)
AMI_ID="""
                file.write(w+q+ami_user+q)
                file.close()
                print
                print " Changed AMI to "+ami_user
                spacetime()
                os.chdir(bm)
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


def uploadproject(projfilename, projfilepath, uploadtype):
    # uploadtype = 0: Uploading just a project file
    #            = 1: Uploading a project file and we will include everything in the "/artwork/in project" directory
    #            = 2: Uploading an already zipped archive
    while True:
        clear()
        print
        print " ***WARNING***"
        print
        print
        print " This will..."
        print
        print
        print " 1. delete all files in your frame and project buckets"
        print
        if (uploadtype == 1):
            print " 2. zip and upload "+projfilename+' as well as any files in the "artwork/in project" directory'
        elif (uploadtype == 2):
            print " 2. upload the already-zipped archive "+projfilename
        else:
            print " 2. zip and upload "+projfilename
        print
        print " 3. reset work queue"
        print
        print
        nprojconf = raw_input(' Do you want to continue, type y or n? ')
        if nprojconf=='y':
            clear()

            #gets various variables
            from os.path import expanduser
            home = expanduser("~")
            os.chdir(home)
            parser = ConfigParser.ConfigParser()
            parser.readfp(FakeSecHead(open('.brenda.conf')))
            #find original values
            a = parser.get('asection', 'INSTANCE_TYPE')
            b = parser.get('asection', 'BLENDER_PROJECT')
            c = parser.get('asection', 'WORK_QUEUE')
            d = parser.get('asection', 'RENDER_OUTPUT')
            e = parser.get('asection', 'DONE')
            f = parser.get('asection', 'FRAME_OR_SUBFRAME')
            g = parser.get('asection', 'TILE')
            h = parser.get('asection', 'NUMBER_INSTANCES')
            i = parser.get('asection', 'PRICE_BID')
            j = parser.get('asection', 'FILE_TYPE')
            k = parser.get('asection', 'START_FRAME')
            l = parser.get('asection', 'END_FRAME')
            m = parser.get('asection', 'AVAILABILITY_ZONE')
            n = parser.get('asection', 'FRAME_LIST_FILE')
            o = parser.get('asection', 'FRAME_LIST_OR_FRAME_RANGE')

            #create new options
            a_nm = 'INSTANCE_TYPE='
            b_nm = 'BLENDER_PROJECT='
            c_nm = 'WORK_QUEUE='
            d_nm = 'RENDER_OUTPUT='
            e_nm = 'DONE='
            f_nm = 'FRAME_OR_SUBFRAME='
            g_nm = 'TILE='
            h_nm = 'NUMBER_INSTANCES='
            i_nm = 'PRICE_BID='
            j_nm = 'FILE_TYPE='
            k_nm = 'START_FRAME='
            l_nm = 'END_FRAME='
            m_nm = 'AVAILABILITY_ZONE='
            n_nm = 'FRAME_LIST_FILE='
            o_nm = 'FRAME_LIST_OR_FRAME_RANGE='
            z = '\n'

            projbucketname = urlparse.urlsplit(b).netloc
            projbucketpath = 's3://'+projbucketname
            print
            print "projbucketpath: " + projbucketpath

            #changes to s3cmd working directory
            print
            print "Changing to s3cmd working directory: " + ps
            os.chdir(ps)


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

            if (uploadtype == 1):
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
                print zippedprojfilename + " has been created"
                print
            elif (uploadtype == 0):
                output = zipfile.ZipFile(zippedprojfilename, 'w')
                output.write(projfilename)
                output.close()
                print zippedprojfilename + " has been created"
                print

            print "Changing to s3cmd working directory: " + ps
            os.chdir(ps)
            print
            print 'python s3cmd put --no-mime-magic --multipart-chunk-size-mb=5 "'+projfilepath+sl+zippedprojfilename+'" '+sb+projbucketpath
            os.system('python s3cmd put --no-mime-magic --multipart-chunk-size-mb=5 "'+projfilepath+sl+zippedprojfilename+'" '+sb+projbucketpath)
            print
            print ' Project file has been uploaded'

            #deletes zipped file from users pc
            if (uploadtype != 2):
                print
                print "Deleting zipped file from user's PC"
                os.chdir(projfilepath)
                os.remove(zippedprojfilename)

            #changes reference in config file
            home = expanduser("~")
            os.chdir(home)
            file = open(".brenda.conf", "w")
            b = projbucketpath+sl+zippedprojfilename
            newconfig = a_nm+a+z+b_nm+b+z+c_nm+c+z+d_nm+d+z+e_nm+e+z+f_nm+f+z+g_nm+g+z+h_nm+h+z+i_nm+i+z+j_nm+j+z+k_nm+k+z+l_nm+l+z+m_nm+m+z+n_nm+n+z+o_nm+o
            file.write(newconfig)
            file.close()
            #status = os.chdir(bm)
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
        qconf = raw_input(' Are these values correct, y or n? ')  
        if qconf=='y':
            clear()
            conf = read_conf_values()
            #new values
            k = sframe
            l = eframe
            o = 'FRAME_RANGE'
            newconfig = conf.a_nm+conf.a+conf.z+conf.b_nm+conf.b+conf.z+conf.c_nm+conf.c+conf.z+conf.d_nm+conf.d+conf.z+conf.e_nm+conf.e+conf.z+conf.f_nm+conf.f+conf.z+conf.g_nm+conf.g+conf.z+conf.h_nm+conf.h+conf.z+conf.i_nm+conf.i+conf.z+conf.j_nm+conf.j+conf.z+conf.k_nm+k+conf.z+conf.l_nm+l+conf.z+conf.m_nm+conf.m+conf.z+conf.n_nm+conf.n+conf.z+conf.o_nm+o
            confwrite(newconfig)
            print
            print ' Frame range changed ( '+k,'- '+l,')'
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

    conf = read_conf_values()
    # new values
    o = 'FRAME_LIST'
    n = framelistfile
    newconfig = conf.a_nm + conf.a + conf.z + conf.b_nm + conf.b + conf.z + conf.c_nm + conf.c + conf.z + conf.d_nm + conf.d + conf.z + conf.e_nm + conf.e + conf.z + conf.f_nm + conf.f + conf.z + conf.g_nm + conf.g + conf.z + conf.h_nm + conf.h + conf.z + conf.i_nm + conf.i + conf.z + conf.j_nm + conf.j + conf.z + conf.k_nm + conf.k + conf.z + conf.l_nm + conf.l + conf.z + conf.m_nm + conf.m + conf.z + conf.n_nm + n + conf.z + conf.o_nm + o
    confwrite(newconfig)

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
        rconf = raw_input(' Would you like to start the job, y or n? ')  
        if rconf == 'n':
            clear()
            print
            print ' Job not started'
            spacetime()
            break
        if rconf =='y':
            clear()
            print
            print ' This will build work queue and initiate instances'
            print 
            print
            doublerconf = raw_input(' Are you sure, y or n? ')

            if doublerconf =='n':
                clear()
                print
                print ' Job not started'
                spacetime()
                break

            if doublerconf == 'y':
                clear()
                os.chdir(bm)
                if conf.f == 'frame':
                    if conf.o == 'FRAME_RANGE': # We have a normal range of frames, so we need to put a "push" at the end of this call
                        queue = py+bw+t+ft+strt+conf.k+sb+end+conf.l+sb+pu
                    else: # FRAME_LIST
                        queue = py+bw+t+ft+frame_script+'"'+conf.n+'"'+sb+push_with_frame_script
                if conf.f == 'subframe':
                    if conf.o == 'FRAME_RANGE': # We have a normal range of frames, so we need to put a "push" at the end of this call
                        queue = py+bw+t+sft+strt+conf.k+sb+end+conf.l+sb+xsize+conf.g+sb+ysize+conf.g+sb+pu
                    else: # FRAME_LIST
                        queue = py+bw+t+sft+frame_script+'"'+conf.n+'"'+sb+xsize+conf.g+sb+ysize+conf.g+sb+push_with_frame_script

                status = os.system(queue)
                print '\n'

                if status == 1:
                    print ' There was an error building work queue'
                    exit = raw_input(' Press Enter to continue ')
                    break

                if status == 0:
                    print ' Work queue has been built'
                    print
                    instrequest = py+br+i+conf.a+sb+n+conf.h+sb+p+conf.i+sb+spot+' '+zFlag+conf.m
                    print instrequest
                    print '\n'
                    status = os.system(instrequest)
                    print
                    print
                    if status == 1:
                        print '\n'
                        print ' There was an error initiating Instances. Try a C3 instance type for this AMI'
                        resetworkqueue()
                        exit = raw_input(' Press Enter to continue ')
                        break
                    if status == 0:
                        print '\n'
                        print ' Instance/s have been initiated'
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
        print " a = " + zonebase + "a"
        print " b = " + zonebase + "b"
        print " c = " + zonebase + "c"
        print " d = " + zonebase + "d"
        print " e = " + zonebase + "e"
        print " f = " + zonebase + "f"
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
        zonetype = zonebase + zone
        print
        print " You are bidding for "+amount,"X"+sb+instype,"in availability zone "+zonetype,"at a cost of $"+price,"per instance."
        print
        amountD = Decimal(amount)
        priceD = Decimal(price)
        math = (amountD*priceD)
        print ' This will cost you $'+ str(math), 'per hour'
        print
        print
        iconf = raw_input(' Are these values correct, y or n? ')  
        if iconf=='y':
            clear()
            conf = read_conf_values()
            #new values
            h = amount
            a = instype
            i = price
            m = zonetype
            newconfig = conf.a_nm+a+conf.z+conf.b_nm+conf.b+conf.z+conf.c_nm+conf.c+conf.z+conf.d_nm+conf.d+conf.z+conf.e_nm+conf.e+conf.z+conf.f_nm+conf.f+conf.z+conf.g_nm+conf.g+conf.z+conf.h_nm+h+conf.z+conf.i_nm+i+conf.z+conf.j_nm+conf.j+conf.z+conf.k_nm+conf.k+conf.z+conf.l_nm+conf.l+conf.z+conf.m_nm+m+conf.z+conf.n_nm+conf.n+conf.z+conf.o_nm+conf.o
            confwrite(newconfig)
            print
            print ' Instance information has been changed to'
            print
            print ' '+h,'x '+a+' using availability zone '+m,'instances @ $'+i,'each per hour'
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
        status = os.chdir(bm)
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
        status = os.chdir(bm)
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
            status = os.system(py+bw+st)      
            print
            print
            exit = raw_input(' Press Enter to continue ')
        if montask=='r':  
            clear()
            print
            os.system(py+br+st)     
            print
            print
            exit = raw_input(' Press Enter to continue ')
        if montask=='u':           
            clear()
            print
            os.system(py+bt+sh+ut)      
            print
            print
            exit = raw_input(' Press Enter to continue ')
        if montask=='l':           
            clear()
            while True:
                print
                os.system(py+bt+sh+tl)
                print
                logInput = raw_input(' Enter m to go back to the previous menu, otherwise press Enter to get more of the log.')
                if logInput == 'm':
                    break
        if montask=='f':
            clear()
            print
            os.system(py+bt+pf)    
            print  
            print
            exit = raw_input(' Press Enter to continue ')
        if montask=='c':           
            clear()
            print
            os.system(py+bt+sh+tc)      
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
                        close = py+bt+t+dflag+smlt+uptime+sb+pru+inprunet
                    if dry =='n':
                        close = py+bt+t+smlt+uptime+sb+pru+inprunet
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
                        close2 = py+bt+t+dflag+pru+inprune
                    if dry =='n':
                        close2 = py+bt+t+pru+inprune
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
            status = os.chdir(ps)
            status = os.system('python s3cmd get -r --skip-existing '+RENDER_OUTPUT+sb+dir)
            clear()
            print
            print " Frames have been downloaded"
            print
            print
            exit = raw_input(' Press Enter to continue ')
            status = os.chdir(bm)
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
                    status = os.chdir(ps)
                    status = os.system('python s3cmd get -r --skip-existing '+RENDER_OUTPUT+sb+dir)
                    status = os.chdir(bm)
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
        status = os.chdir(bm)
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
            econf = raw_input(' Would you like to (among other things) empty frame and project buckets, y or n? ')  
            if econf =='y':
                clear()
                print
                print ' This operation will (among other things) delete all files in your frame and project buckets!'
                print 
                print
                doubleeconf = raw_input(' Are you sure, y or n? ')                
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
            econf = raw_input(' Would you like to empty frame and project buckets, y or n? ')  
            if econf =='y':
                clear()
                print
                print ' This will delete all files in your frame and project buckets!'
                print 
                print
                doubleeconf = raw_input(' Are you sure, y or n? ')
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
    s3cmd_there = os.path.isfile(home+ap+ini)
    if s3cmd_there == False:
        clear()
        shutil.copyfile(home+sl+scf, home+ap+scf)
        os.rename(home+ap+scf, home+ap+ini)

#This changes a line in the "tool.py" file as new Ubuntu AMIs only let you ssh in as "ubuntu" and not "tool" whereas old Ubuntu AMIs let you log in as both
def toolchange ():
    x = 'tool.py'
    with open(bm+sl+brenda+sl+x, 'r') as file:
        data = file.readlines()
    data[73] = """                user = utils.get_opt(opts.user, conf, 'AWS_USER', default='ubuntu')\n"""
    with open(bm+sl+brenda+sl+x, 'w') as file:
        file.writelines( data )

#This checks frame and subframe options in .conf file
def confadd ():
    from os.path import expanduser
    home = expanduser("~")
    os.chdir(home)

    print
    print "Looking for config file here: " + home
    print

    parser = ConfigParser.ConfigParser()
    parser.readfp(FakeSecHead(open('.brenda.conf')))
    fos = parser.has_option('asection', 'FRAME_OR_SUBFRAME')
    if fos == False:
        #find original values
        a = parser.get('asection', 'INSTANCE_TYPE')
        b = parser.get('asection', 'BLENDER_PROJECT')
        c = parser.get('asection', 'WORK_QUEUE')
        d = parser.get('asection', 'RENDER_OUTPUT')
        e = parser.get('asection', 'DONE')
        m = parser.get('asection', 'AVAILABILITY_ZONE')
        n = parser.get('asection', 'FRAME_LIST_FILE')
        o = parser.get('asection', 'FRAME_LIST_OR_FRAME_RANGE')
        #new values
        f = 'frame'
        g = 'non'
        h = '0'
        i = '0.00'
        j = 'png'
        k = '0'
        l = '0'

        #create new options
        a_nm = 'INSTANCE_TYPE='
        b_nm = 'BLENDER_PROJECT='
        c_nm = 'WORK_QUEUE='
        d_nm = 'RENDER_OUTPUT='
        e_nm = 'DONE='
        f_nm = 'FRAME_OR_SUBFRAME='
        g_nm = 'TILE='
        h_nm = 'NUMBER_INSTANCES='
        i_nm = 'PRICE_BID='
        j_nm = 'FILE_TYPE='
        k_nm = 'START_FRAME='
        l_nm = 'END_FRAME='
        m_nm = 'AVAILABILITY_ZONE='
        n_nm = 'FRAME_LIST_FILE='
        o_nm = 'FRAME_LIST_OR_FRAME_RANGE='
        z = '\n'
        #write to file
        newconfig = a_nm+a+z+b_nm+b+z+c_nm+c+z+d_nm+d+z+e_nm+e+z+f_nm+f+z+g_nm+g+z+h_nm+h+z+i_nm+i+z+j_nm+j+z+k_nm+k+z+l_nm+l+z+m_nm+m+z+n_nm+n+z+o_nm+o
        file = open(".brenda.conf", "w")
        file.write(newconfig)
        file.close()



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
            #new values
            f = 'frame'
            g = 'non'
            #write to file
            newconfig = conf.a_nm+conf.a+conf.z+conf.b_nm+conf.b+conf.z+conf.c_nm+conf.c+conf.z+conf.d_nm+conf.d+conf.z+conf.e_nm+conf.e+conf.z+conf.f_nm+f+conf.z+conf.g_nm+g+conf.z+conf.h_nm+conf.h+conf.z+conf.i_nm+conf.i+conf.z+conf.j_nm+conf.j+conf.z+conf.k_nm+conf.k+conf.z+conf.l_nm+conf.l+conf.z+conf.m_nm+conf.m+conf.z+conf.n_nm+conf.n+conf.z+conf.o_nm+conf.o
            confwrite(newconfig)
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
                    #new value
                    f = 'subframe'
                    g = '8'
                    #write to file
                    newconfig = conf.a_nm+conf.a+conf.z+conf.b_nm+conf.b+conf.z+conf.c_nm+conf.c+conf.z+conf.d_nm+conf.d+conf.z+conf.e_nm+conf.e+conf.z+conf.f_nm+f+conf.z+conf.g_nm+g+conf.z+conf.h_nm+conf.h+conf.z+conf.i_nm+conf.i+conf.z+conf.j_nm+conf.j+conf.z+conf.k_nm+conf.k+conf.z+conf.l_nm+conf.l+conf.z+conf.m_nm+conf.m+conf.z+conf.n_nm+conf.n+conf.z+conf.o_nm+conf.o
                    confwrite(newconfig)
                    print
                    print ' Changed to sub-frame rendering with '+g+x+g,'tile size'
                    spacetime()
                    break

                if tilechoice =='b':
                    #new value
                    f = 'subframe'
                    g = '4'
                    #write to file
                    newconfig = conf.a_nm+conf.a+conf.z+conf.b_nm+conf.b+conf.z+conf.c_nm+conf.c+conf.z+conf.d_nm+conf.d+conf.z+conf.e_nm+conf.e+conf.z+conf.f_nm+f+conf.z+conf.g_nm+g+conf.z+conf.h_nm+conf.h+conf.z+conf.i_nm+conf.i+conf.z+conf.j_nm+conf.j+conf.z+conf.k_nm+conf.k+conf.z+conf.l_nm+conf.l+conf.z+conf.m_nm+conf.m+conf.z+conf.n_nm+conf.n+conf.z+conf.o_nm+conf.o
                    confwrite(newconfig)
                    print
                    print ' Changed to sub-frame rendering with '+g+x+g,'tile size'
                    spacetime()
                    break
                if tilechoice =='c':
                    #new value
                    f = 'subframe'
                    g = '2'
                    #write to file
                    newconfig = conf.a_nm+conf.a+conf.z+conf.b_nm+conf.b+conf.z+conf.c_nm+conf.c+conf.z+conf.d_nm+conf.d+conf.z+conf.e_nm+conf.e+conf.z+conf.f_nm+f+conf.z+conf.g_nm+g+conf.z+conf.h_nm+conf.h+conf.z+conf.i_nm+conf.i+conf.z+conf.j_nm+conf.j+conf.z+conf.k_nm+conf.k+conf.z+conf.l_nm+conf.l+conf.z+conf.m_nm+conf.m+conf.z+conf.n_nm+conf.n+conf.z+conf.o_nm+conf.o
                    confwrite(newconfig)
                    print
                    print ' Changed to sub-frame rendering with '+g+x+g,'tile size'
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
                    j = 'PNG'
                    clear()
                    frametemplateformat(sb+ff+sb+j+sb)
                    subframetemplateformat(sb+ff+sb+j+sb)
                    #write to file
                    newconfig = conf.a_nm+conf.a+conf.z+conf.b_nm+conf.b+conf.z+conf.c_nm+conf.c+conf.z+conf.d_nm+conf.d+conf.z+conf.e_nm+conf.e+conf.z+conf.f_nm+conf.f+conf.z+conf.g_nm+conf.g+conf.z+conf.h_nm+conf.h+conf.z+conf.i_nm+conf.i+conf.z+conf.j_nm+j+conf.z+conf.k_nm+conf.k+conf.z+conf.l_nm+conf.l+conf.z+conf.m_nm+conf.m+conf.z+conf.n_nm+conf.n+conf.z+conf.o_nm+conf.o
                    confwrite(newconfig)
                    clear()
                    print
                    print ' Changed frame format to '+j
                    spacetime()
                    break

                if formatchoice=='e':
                    j = 'EXR'
                    clear()
                    frametemplateformat(sb+ff+sb+j+sb)
                    subframetemplateformat(sb+ff+sb+j+sb)
                    #write to file
                    newconfig = conf.a_nm+conf.a+conf.z+conf.b_nm+conf.b+conf.z+conf.c_nm+conf.c+conf.z+conf.d_nm+conf.d+conf.z+conf.e_nm+conf.e+conf.z+conf.f_nm+conf.f+conf.z+conf.g_nm+conf.g+conf.z+conf.h_nm+conf.h+conf.z+conf.i_nm+conf.i+conf.z+conf.j_nm+j+conf.z+conf.k_nm+conf.k+conf.z+conf.l_nm+conf.l+conf.z+conf.m_nm+conf.m+conf.z+conf.n_nm+conf.n+conf.z+conf.o_nm+conf.o
                    confwrite(newconfig)
                    clear()
                    print
                    print ' Changed frame format to '+j
                    spacetime()
                    break

                if formatchoice=='j':
                    j = 'JPEG'
                    clear()
                    frametemplateformat(sb+ff+sb+j+sb)
                    subframetemplateformat(sb+ff+sb+j+sb)                
                    #write to file
                    newconfig = conf.a_nm+conf.a+conf.z+conf.b_nm+conf.b+conf.z+conf.c_nm+conf.c+conf.z+conf.d_nm+conf.d+conf.z+conf.e_nm+conf.e+conf.z+conf.f_nm+conf.f+conf.z+conf.g_nm+conf.g+conf.z+conf.h_nm+conf.h+conf.z+conf.i_nm+conf.i+conf.z+conf.j_nm+j+conf.z+conf.k_nm+conf.k+conf.z+conf.l_nm+conf.l+conf.z+conf.m_nm+conf.m+conf.z+conf.n_nm+conf.n+conf.z+conf.o_nm+conf.o
                    confwrite(newconfig)
                    clear()
                    print
                    print ' Changed frame format to '+j
                    spacetime()
                    break

                if formatchoice=='t':
                    j = 'TIFF'
                    clear()
                    frametemplateformat(sb+ff+sb+j+sb)
                    subframetemplateformat(sb+ff+sb+j+sb)
                    #write to file
                    newconfig = conf.a_nm+conf.a+conf.z+conf.b_nm+conf.b+conf.z+conf.c_nm+conf.c+conf.z+conf.d_nm+conf.d+conf.z+conf.e_nm+conf.e+conf.z+conf.f_nm+conf.f+conf.z+conf.g_nm+conf.g+conf.z+conf.h_nm+conf.h+conf.z+conf.i_nm+conf.i+conf.z+conf.j_nm+j+conf.z+conf.k_nm+conf.k+conf.z+conf.l_nm+conf.l+conf.z+conf.m_nm+conf.m+conf.z+conf.n_nm+conf.n+conf.z+conf.o_nm+conf.o
                    confwrite(newconfig)
                    clear()
                    print
                    print ' Changed frame format to '+j
                    spacetime()
                    break

                if formatchoice=='f':
                    frametemplateformat(sb)
                    subframetemplateformat(sb)
                    #new values
                    j = 'specifiedinfile'
                    #write to file
                    newconfig = conf.a_nm+conf.a+conf.z+conf.b_nm+conf.b+conf.z+conf.c_nm+conf.c+conf.z+conf.d_nm+conf.d+conf.z+conf.e_nm+conf.e+conf.z+conf.f_nm+conf.f+conf.z+conf.g_nm+conf.g+conf.z+conf.h_nm+conf.h+conf.z+conf.i_nm+conf.i+conf.z+conf.j_nm+j+conf.z+conf.k_nm+conf.k+conf.z+conf.l_nm+conf.l+conf.z+conf.m_nm+conf.m+conf.z+conf.n_nm+conf.n+conf.z+conf.o_nm+conf.o
                    confwrite(newconfig)
                    clear()
                    print
                    print ' Changed to format specified in uploaded .blend file'
                    spacetime()
                    break

# Note: Added the flag "--enable-autoexec" to the frame and subframe template.
#       This is the equivalent of going into User Preferences, File and checking "Auto Execution: Auto Run Python Scripts".
#       If this option is not turned on and you are using BlenRig, the armature won't run correctly (FK arms and forearms will stay completely straight).
def frametemplateformat(newformat):
    os.chdir(bm)
    fpart = 'blender -b *.blend --enable-autoexec'
    lpart = '-o $OUTDIR/frame_###### -s $START -e $END -j $STEP -t 0 -a'
    file = open("frame-template", "w")
    file.write(fpart+newformat+lpart)
    file.close()

def subframetemplateformat(newformat):
    os.chdir(bm)
    fpart = """cat >subframe.py <<EOF
import bpy
bpy.context.scene.render.border_min_x = $SF_MIN_X
bpy.context.scene.render.border_max_x = $SF_MAX_X
bpy.context.scene.render.border_min_y = $SF_MIN_Y
bpy.context.scene.render.border_max_y = $SF_MAX_Y
bpy.context.scene.render.use_border = True
EOF
blender -b *.blend --enable-autoexec -P subframe.py"""
    lpart = """-o $OUTDIR/frame_######_X-$SF_MIN_X-$SF_MAX_X-Y-$SF_MIN_Y-$SF_MAX_Y -s $START -e $END -j $STEP -t 0 -a"""
    file = open("subframe-template", "w")
    file.write(fpart+newformat+lpart)
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
        self.z = '\n'
        os.chdir(bm)


def confwrite(newconfig):
    from os.path import expanduser
    home = expanduser("~")
    os.chdir(home)
    file = open(".brenda.conf", "w")
    file.write(newconfig)
    file.close()
    os.chdir(bm)



def resetworkqueue():
    os.chdir(bm)
    status = os.system(py+bw+rs)
    if status==0:
        print
        print " Work queue has been reset"
        print
    if status==1:
        print
        print
        print
        print " There was a problem resetting work queue, please try waiting 60 seconds"
    os.chdir(bm)

def stopinstances ():
    print
    status = os.system(py+br+t+sp)
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
    status = os.system(py+br+ca)
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
    a = parser.get('asection', 'INSTANCE_TYPE')
    b = parser.get('asection', 'BLENDER_PROJECT')
    c = parser.get('asection', 'WORK_QUEUE')
    d = parser.get('asection', 'RENDER_OUTPUT')
    e = parser.get('asection', 'DONE')
    f = parser.get('asection', 'FRAME_OR_SUBFRAME')
    g = parser.get('asection', 'TILE')
    h = parser.get('asection', 'NUMBER_INSTANCES')
    i = parser.get('asection', 'PRICE_BID')
    j = parser.get('asection', 'FILE_TYPE')
    k = parser.get('asection', 'START_FRAME')
    l = parser.get('asection', 'END_FRAME')
    m = parser.get('asection', 'AVAILABILITY_ZONE')
    n = parser.get('asection', 'FRAME_LIST_FILE')
    o = parser.get('asection', 'FRAME_LIST_OR_FRAME_RANGE')

    #create new options
    a_nm = 'INSTANCE_TYPE='
    b_nm = 'BLENDER_PROJECT='
    c_nm = 'WORK_QUEUE='
    d_nm = 'RENDER_OUTPUT='
    e_nm = 'DONE='
    f_nm = 'FRAME_OR_SUBFRAME='
    g_nm = 'TILE='
    h_nm = 'NUMBER_INSTANCES='
    i_nm = 'PRICE_BID='
    j_nm = 'FILE_TYPE='
    k_nm = 'START_FRAME='
    l_nm = 'END_FRAME='
    m_nm = 'AVAILABILITY_ZONE='
    n_nm = 'FRAME_LIST_FILE='
    o_nm = 'FRAME_LIST_OR_FRAME_RANGE='
    z = '\n'

    projbucketname = urlparse.urlsplit(b).netloc
    projbucketpath = 's3://'+projbucketname

    #changes to s3cmd working directory
    os.chdir(ps)

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


def subframecreate ():
    status = os.chdir(bm)
    subframe_template_there = os.path.isfile('subframe-template')
    if subframe_template_there == False:
        file = open("subframe-template", "w")
        file.write("""cat >subframe.py <<EOF
import bpy
bpy.context.scene.render.border_min_x = $SF_MIN_X
bpy.context.scene.render.border_max_x = $SF_MAX_X
bpy.context.scene.render.border_min_y = $SF_MIN_Y
bpy.context.scene.render.border_max_y = $SF_MAX_Y
bpy.context.scene.render.use_border = True
EOF
blender -b *.blend -P subframe.py -F PNG -o $OUTDIR/frame_######_X-$SF_MIN_X-$SF_MAX_X-Y-$SF_MIN_Y-$SF_MAX_Y -s $START -e $END -j $STEP -t 0 -a""")
        file.close()

def printspotrequest(spinstype):
    spotrequest = py+br+i+spinstype+sb+spotprice
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

subframecreate()
toolchange()
inidup()
confadd()
mainmenu()
