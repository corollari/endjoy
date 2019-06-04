import inotify.adapters
import os 
import sys
import time
import threading
from pathlib import Path

serverPipeName="/tmp/sendjoy.pipe"
clientPipeName="/tmp/cendjoy.pipe"

checkpoints={}
changes=[]

def main():
    cmd=sys.argv[1]
    if cmd=="start":
        print(start())
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

def processMsg(args):
    cmd=args[0]
    print(args)
    if cmd=="revert":
        return revert(args[1])
    elif cmd=="checkpoint":
        return checkpoint(args[1])
    elif cmd=="suicide":
        return suicide()
    else:
        return "Command not accepted"

def start():
    try: #TODO: Check if already running
        os.mkfifo(serverPipeName)
        os.mkfifo(clientPipeName)
    except:
        return "Already running"
    if os.fork()!=0:
        return "Monitoring started"
    threading.Thread(target=monitor, args=(os.getcwd(),)).start() #Start monitoring
    while True: #Set up IPC
        with open(serverPipeName, 'r') as readPipe:
            with open(clientPipeName, 'w') as writePipe:
                while True:
                    data = readPipe.read()
                    if len(data)==0:
                        break
                    else:
                        msg=processMsg(data.split('#'))
                        writePipe.write(msg)

def revert(to):
    restoreTime=checkpoints.get(name, default = time.time()-string2secs(name))
    i=len(changes)
    while(changes[i]['time']>restoreTime): #FIXME: This doesn't handle properly the possibility of reverting twice
        applyChange(changes[i])
        i-=1
    return "Restored"

def applyChange(change):
    pass

def string2seconds(time):
    mult=1
    if time[-1]=="m":
        mult=60
    elif time[-1]=="h":
        mult=60*60
    return int(time[:-1])*mult

def checkpoint(name):
    checkpoints[name]=time.time()
    return "Checkpoint set"

def suicide():
    os.remove(serverPipeName)
    os.remove(clientPipeName)
    sys.exit(0)

def monitor(path):
    i = inotify.adapters.InotifyTree(path)

    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event
        changes.append({'path':path, 'filename':filename, 'time': time.time(), 'events':type_names})
        # print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(path, filename, type_names))

if __name__ == '__main__':
    main()
