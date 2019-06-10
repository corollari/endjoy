# endjoy

> Ctrl-Z for the filesystem

## What is endjoy?
Endjoy is a command line program that allows you to restore all the files in a directory to the state they were in some time ago. Therefore, it allows you to revert modifications, deletions and creations of the files in the watched directory.  
With this you can just try out any changes without fear, as you can always revert them with a single command.

## Install
```bash
sudo pip install endjoy
```

## Usage

```bash
ej start # Start recursively monitoring the working directory

# Modify/create/delete some files or directories...

ej revert 5m # Revert changes done in the last five minutes
ej revert 1h # Revert changes done in the last hour

ej checkpoint NAME # Checkpoint the current state of the directory
ej checkpoint # List all the stored checkpoints

# Modify some more files

ej revert NAME # Revert the directory to how it was when the checkpoint NAME was created

ej suicide # Stop monitoring the directory and delete all temporary files created
```

## What makes endjoy different from git?
> tl;dr: endjoy is git stash on steroids

The most important difference between git and endjoy is that the latter runs in the background whereas git doesn't, this means that:
- Doesn't require setting explicit checkpoints as with `git commit`
- Runs asynchronously, so you don't have to wait for `git` to finish
- Doesn't require any action till you need to use it to restore a previous state

If you need complex functionality, like merging different commits/checkpoints or moving forward and backwards between them, git is a better choice, as endjoy is much simpler and doesn't implement that

## Why is it called endjoy?
![See https://battleangel.fandom.com/wiki/Endjoy](https://raw.githubusercontent.com/corollari/endjoy/master/endjoy.png)

## Development
Install from source (requires poetry):
```bash
# Optional
virtualenv --python=python3 venv
. venv/bin/activate
# Required
poetry install
# Run
ej
# Run tests
pytest
```

## How does it work?
On `start` it spawns a process, that will act as the server, with two threads:
- One thread subscribes to be notified of changes on all the directories especified via [inotify](http://man7.org/linux/man-pages/man7/inotify.7.html) and stores all the changes along with a timestamp in shared memory
- Another thread creates a named pipe and listens on it, when endjoy is called again with another command this thread performs whatever command was issued using the data that has been gathered by the first thread (inotify one)

## Authors
[@luis136](https://github.com/luis136) and [@corollari](https://github.com/corollari)

## License
[The Unlicense](https://raw.githubusercontent.com/corollari/endjoy/master/LICENSE)
