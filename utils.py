import os
import time
import threading

# Utility Functions
def is_valid_file(parser, file):
    """
    Checks if the file exists, erroring if it doesn't.
    """
    if not os.path.exists(file):
        parser.error("The file %s does not exist!" % file)
    else:
        return file

def wait(threads):
    while threads != []:
        threads = [t for t in threads if t.isAlive()]
        time.sleep(.1)
