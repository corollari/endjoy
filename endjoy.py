import inotify.adapters
import os 

def main(path):
    i = inotify.adapters.InotifyTree(path)

    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event

        print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(
              path, filename, type_names))

if __name__ == '__main__':
    main(os.getcwd())
