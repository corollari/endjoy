# endjoy

> git stash on steroids

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

## Why the name?
![See https://battleangel.fandom.com/wiki/Endjoy](https://raw.githubusercontent.com/corollari/endjoy/master/endjoy.png)
