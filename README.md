# endjoy

> Ctrl-Z for the filesystem

## Install
```bash
sudo pip install endjoy
```

## How to

```bash
endjoy start # Start recursively monitoring the working directory

# Modify/create/delete some files or directories...

endjoy revert 5m # Revert changes done in the last five minutes
endjoy revert 1h # Revert changes done in the last hour

endjoy checkpoint NAME # Checkpoint the current state of the directory
endjoy checkpoint # List all the stored checkpoints

# Modify some more files

endjoy revert NAME # Revert the directory to how it was when the checkpoint NAME was created

endjoy suicide # Stop monitoring the directory and delete all temporary files created
```

## endjoy vs git
> tl;dr: endjoy is git stash on steroids

Endjoy runs in the background whereas git doesn't, this means that:
- Doesn't require setting explicit checkpoints as with `git commit`
- Runs asynchronously, so you don't have to wait for `git` to finish
- Doesn't require any action till you need to use it to restore a previous state

If you need complex functionality, like merging different commits/checkpoints or moving forward and backwards between them, git is a better choice, as endjoy is much simpler and doesn't implement that

## Why the name?
![See https://battleangel.fandom.com/wiki/Endjoy](https://raw.githubusercontent.com/corollari/endjoy/master/endjoy.png)

## Development
Install from source:
```bash
# Optional
virtualenv --python=python3 venv
. venv/bin/activate
# Required
pip install -r requirements.txt
# Run
python endjoy.py
```

## How does it work?
On `start` it spawns a process, that will act as the server, with two threads:
- One thread subscribes to be notified of changes on all the directories especified via [inotify](http://man7.org/linux/man-pages/man7/inotify.7.html) and stores all the changes along with a timestamp in shared memory
- Another thread creates a named pipe and listens on it, when endjoy is called again with another command this thread performs whatever command was issued using the data that has been gathered by the first thread (inotify one)

## Authors
[@luis136](https://github.com/luis136) and [@corollari](https://github.com/corollari)

## License
[The Unlicense](https://raw.githubusercontent.com/corollari/endjoy/master/LICENSE)
