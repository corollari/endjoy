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
from subprocess import run

class Change:
    
    def __init__(self, path, filename, event, timestamp, tempDir):
        self.path = os.path.join(path, filename)
        self.filename = filename
        self.event = event
        self.timestamp = timestamp
        tempFile=os.path.join(tempDir, filename) #FIXME: Doesn't handle files in directories 
        self.tempFile=tempFile

        if 'IN_MOVED_TO' in self.event:
            if not Path(tempFile).exists():
                self.event.append('IN_CREATE')
            self.event.append('IN_MODIFY')
        if 'IN_MOVED_FROM' in self.event:
            self.event.append('IN_DELETE')

        if 'IN_CREATE' in self.event:
            Path(tempFile).touch()
        if 'IN_MODIFY' in self.event:
            self.diff=str(run(['diff', '-u', self.path, tempFile], capture_output=True).stdout.decode("utf-8"))
            run(['cp', self.path, tempFile])
        if 'IN_DELETE' in self.event:
            self.contents=open(tempFile, 'r').read()
            os.remove(tempFile)

    def __str__(self):
      return str(self.timestamp)

    def setDiff():
      pass

    def unDo(self):
        # print(self.event)
        if 'IN_DELETE' in self.event:
            # print("create %s"%self.path)
            open(self.path, 'w+').write(self.contents)
            open(self.tempFile, 'w+').write(self.contents)
        if 'IN_MODIFY' in self.event:
            # print("modify %s"%self.path)
            # print(self.diff)
            run(['patch', '-f', '-s'], input=self.diff, encoding='utf-8')
            run(['cp', self.path, self.tempFile])
        if 'IN_CREATE' in self.event:
            # print("delete %s"%self.path)
            os.remove(self.path)
            os.remove(self.tempFile)

serverPipeName="/tmp/sendjoy.pipe"
clientPipeName="/tmp/cendjoy.pipe"

reverting=False

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
    if cmd=="revert":
        return revert(args[1])
    elif cmd=="checkpoint":
        return checkpoint(args[1] if len(args)>=2 else None)
    elif cmd=="suicide":
        sys.exit(0)
    else:
        return "Command not accepted"

def recursiveCopy(src,dst):
    os.chdir(src)
    for item in os.listdir():
        os.chdir(src)
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
    cwd=os.getcwd()
    recursiveCopy(cwd, tempDir)
    threading.Thread(target=monitor, args=(cwd,tempDir,), daemon=True).start() #Start monitoring
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
    try:
        os.remove(serverPipeName)
    except:
        pass
    try:
        os.remove(clientPipeName)
    except:
        pass

def revert(to):
    global changes, reverting
    if to in checkpoints:
        restoreTime=checkpoints[to]
    else:
        restoreTime=time.time()-string2secs(to)
    i=len(changes)-1
    reverting=True
    while(i>=0 and changes[i].timestamp>restoreTime):
        changes[i].unDo()
        i-=1
    changes = changes[:i] # TODO: Allow redoing changes instead of only undoing 
    reverting=False
    return "Restored"

def string2secs(time):
    mult=1
    if time[-1]=="m":
        mult=60
    elif time[-1]=="h":
        mult=60*60
    return int(time[:-1])*mult

def checkpoint(name):
    if name==None:
        return "\n".join(["%s - %d seconds ago"%(k, time.time()-checkpoints[k]) for k in checkpoints.keys()])
    checkpoints[name]=time.time()
    return "Checkpoint set"

def suicide(tempDir):
    print("Suicided")
    os.remove(serverPipeName)
    os.remove(clientPipeName)
    shutil.rmtree(tempDir)

def monitor(path, tempDir):
    i = inotify.adapters.InotifyTree(path)

    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event
        EVENTS_USED=['IN_MOVED_TO', 'IN_MOVED_FROM', 'IN_CREATE', 'IN_MODIFY', 'IN_DELETE']
        if not reverting and any(ev in EVENTS_USED for ev in type_names):
            # print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(path, filename, type_names))
            changes.append(Change(path, filename, type_names, time.time(), tempDir))

if __name__ == '__main__':
    main()
