#!/usr/bin/python3
# vim: set cc=80 tw=79:
# Joseph Harriott  http://momentary.eu/  mar 13 juin 2017

"""
Print to file the differences in two directory structures.

Looking recursively in pairs of directories (which are defined below),
find differences in file contents, and list those files with their paths
(and size in bytes), alphabetically sorted.
If Run in Terminal is chosen, see an indication of progress printed.

There should be an environment variable  machineName
which matches a folder alongside this script,
in which is the input file and will be the output file.

Input file ("<this_script's_basename>0.txt")
should contain matched directory pairs, like this:
/run/media/jo/SAMSUNG/AV-Stack /mnt/WD30EZRZ/AV-Stack
# comments out lines.

in Bash, run like this:
python3 /mnt/SDSSDA240G/More/IT_stack/RecursivComp/RecursivComp.py
python3 /media/jo/BX200/Dropbox/JH/IT_stack/RecursivComp/RecursivComp.py
python3 $ITstack/onGitHub/RecursivComp/RecursivComp.py
"""
import datetime
import os
import socket
import sys
import time

# get two timestamps:
start = time.time()
startd = datetime.datetime.now().isoformat(' ')

# Setup a list of folder pairs
# ----------------------------
ifloc = os.environ["machineName"]
# get the input filename (taken from this script's own name):
thisScript = sys.argv[0].replace('./', '')
tS_here = thisScript.rsplit('/', 1)[1]
iflnm = sys.path[0]+'/'+ifloc+'/'+tS_here.replace('.py', '-Pairs.txt')
print('- will use', iflnm)
# get the folder pair list from it:
fpairs = [iline.rstrip('\n') for iline in open(iflnm)]


# function to create file lists with relative paths included:
def filelister(listdir):
    # initialise a list just with the base folder path:
    flrc = 0
    fileList = [listdir]
    print(' Looking at contents of', fileList[0])
    for root, folders, files in os.walk(listdir):
        for file in files:
            # indication of progress:
            flrc += 1
            # print(flrc, end='\r', flush=True)
            # - works, but Flake8 reports as invalid syntax E901, so:
            sys.stdout.write('\r  ' + str(flrc))
            sys.stdout.flush()
            abspath = os.path.join(root, file)
            # take listdir out of the printout:
            fileList.append(abspath.replace(listdir + "/", "") +
                            # add file's bytesize:
                            "  ("+str(os.path.getsize(abspath))+" bytes)")
    return fileList, flrc


# Begin the output file:
# using an output filename taken from this script's own name:
oflnm = iflnm.replace('Pairs', 'Done')
# create a file object for output:
fo = open(oflnm, 'w')
# create a nice header:
wrt1 = socket.gethostname()+' disks: folder changes at '+startd+'\n\n'
fo.write(wrt1)

# Now get the lists of files, compare them, and write the differences:
for ifldr in range(0, int(len(fpairs))):
    if fpairs[ifldr][0] != '#':
        fpair = fpairs[ifldr].split()
        print(fpair[0], "<=>", fpair[1])
        if os.path.isdir(fpair[0]) and os.path.isdir(fpair[1]):
            #
            # Initialise the lists
            fhead = ['']*2
            # (one for each folder-pair, and one for their diff-list):
            flist = [[], [], []]
            # and the two counts:
            flc = [0]*2
            # get the folder-pairs, with counts:
            for fpi in range(2):
                flist[fpi], flc[fpi] = filelister(fpair[fpi])
                print(' - file records loaded in.')
                # pull off the first item (root folder name)
                #   and append the count:
                fhead[fpi] = flist[fpi].pop(0) + ' - contains '+str(flc[fpi])
                fhead[fpi] += ' files, these ones unmatched:'
            #
            # Identify the index of the list to be picked through:
            # it can be the 2nd list:
            d = 1
            # but not if the 1st is shorter:
            if flc[0] < flc[1]:
                d = 0
            # Get the index for the other (possibly longer) list:
            dl = abs(d-1)
            #
            # working through first list,
            #   eliminate items duplicated in the second,
            # leaving two lists of unmatched items:
            print(' Looking for differences in the records now...')
            for ircomp in range(1, flc[d]+1):
                # Pull off the first item from the pick-list:
                item = flist[d].pop(0)
                # print an indication of progress:
                sys.stdout.write('\r  ' + str(ircomp))
                sys.stdout.flush()
                try:
                    flist[dl].remove(item)
                except ValueError:
                    flist[2].append(item)
            flist[dl].sort()
            flist[2].sort()
            print(' - subdirectory records compared')
            # write the resulting unmatched items:
            wrt2 = fhead[dl]
            if len(flist[dl]) > 0:
                wrt2 += '\n'+'\n'.join(flist[dl])
            wrt2 += '\n\n'+fhead[d]
            if len(flist[2]) > 0:
                wrt2 += '\n'+'\n'.join(flist[2])
            # and the time taken:
            wrt3 = '\n\n- took '+str(time.time()-start)
            wrt3 += ' seconds to find the differences.'+'\n\n'
            fo.write('\n'+wrt2+wrt3)
        else:
            print(' not there')
print('- all done, results are in \'' + oflnm + '\'.')

# write and close the file object:
fo.close()
