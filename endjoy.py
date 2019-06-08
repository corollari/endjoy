#!/usr/bin/env python3
import inotify.adapters
import os 
import sys
import time
import threading
from pathlib import Path
import tempfile
import shutil
import atexit
import signal

class Change:
    
    def __init__(self, path, filename, event, timestamp):
      #TODO: diff
      self.path = path
      self.filename = filename
      self.event = event
      self.timestamp = timestamp

    def __str__(self):
      return str(self.timestamp)

    def setDiff():
      pass

    def unDo():
      pass

serverPipeName="/tmp/sendjoy.pipe"
clientPipeName="/tmp/cendjoy.pipe"

checkpoints={}
changes=[]

def main():
    if len(sys.argv)<2:
        print("No command given")
        return
    cmd=sys.argv[1]
    if cmd=="start":
        print(start())
    elif cmd=="clear":
        clear()
        print("Cleared artifacts")
    else:
        try:
            if not Path(serverPipeName).exists():
                raise
            open(serverPipeName, 'w').write("#".join(sys.argv[1:]))
            if cmd!="suicide":
                print(open(clientPipeName, 'r').read())
            else:
                open(clientPipeName, 'r')
        except:
            print("The server is not running, have you started endjoy?")

def processMsg(args, tempDir):
    cmd=args[0]
    print(args)
    if cmd=="revert":
        return revert(args[1])
    elif cmd=="checkpoint":
        return checkpoint(args[1])
    elif cmd=="suicide":
        sys.exit(0)
    else:
        return "Command not accepted"

def recursiveCopy(src,dst):
    os.chdir(src)
    for item in os.listdir():
        if os.path.isfile(item):
            shutil.copy(item, dst)
        elif os.path.isdir(item):
            newFolder = os.path.join(dst, item)
            os.mkdir(newFolder)
            recursiveCopy(os.path.abspath(item), newFolder)

def handle_exit(sig, frame):
    print('endjoy process has been terminated')
    sys.exit(0)

def start():
    try: #TODO: Check if already running
        os.mkfifo(serverPipeName)
        os.mkfifo(clientPipeName)
    except:
        return "Already running"

    tempDir = tempfile.mkdtemp(prefix="endjoy_")


    if os.fork()!=0:
        return "Monitoring started"
    atexit.register(suicide, tempDir)
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)
    recursiveCopy(os.getcwd(),tempDir)
    threading.Thread(target=monitor, args=(os.getcwd(),), daemon=True).start() #Start monitoring
    while True: #Set up IPC
        with open(serverPipeName, 'r') as readPipe:
            with open(clientPipeName, 'w') as writePipe:
                while True:
                    data = readPipe.read()
                    if len(data)==0:
                        break
                    else:
                        msg=processMsg(data.split('#'), tempDir)
                        writePipe.write(msg)

def clear():
    os.remove(serverPipeName)
    os.remove(clientPipeName)

def revert(to):
    restoreTime=checkpoints.get(to, time.time()-string2secs(to))
    i=len(changes)-1
    while(i>=0 and changes[i]['time']>restoreTime): #FIXME: This doesn't handle properly the possibility of reverting twice
        applyChange(changes[i])
        i-=1
    return "Restored"

def applyChange(change):
    pass

def string2secs(time):
    mult=1
    if time[-1]=="m":
        mult=60
    elif time[-1]=="h":
        mult=60*60
    return int(time[:-1])*mult

def checkpoint(name):
    checkpoints[name]=time.time()
    return "Checkpoint set"

def suicide(tempDir):
    print("suicided")
    os.remove(serverPipeName)
    os.remove(clientPipeName)
    shutil.rmtree(tempDir)

def monitor(path):
    i = inotify.adapters.InotifyTree(path)

    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event
        # changes.append({'path':path, 'filename':filename, 'time': time.time(), 'events':type_names})
        # print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(path, filename, type_names))
        changes.append(Change(path, filename, type_names, time.time()))

if __name__ == '__main__':
    main()
