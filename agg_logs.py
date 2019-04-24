import json
from utils import is_valid_file
import os
import argparse


def main():
    parser = argparse.ArgumentParser(description='Reads in the json of log locations.')
    parser.add_argument('-i', type=lambda x: is_valid_file(parser, x), default="default.json",
                        help='Identity_file for the host you would like to get logs from.')
    parser.add_argument('-f', type=lambda x: is_valid_file(parser, x), default="default.json",
                        help='Pass in a JSON detailing where to fetch the logs from')
    parser.add_argument('-db', action='store_true',
                        help='prints out commands instead of executing to debug')

    args = parser.parse_args()
    file, debug = args.f, args.db
    # Aggregate logs
    with open(file) as f:
        logDir = json.load(f)
    id = ''
    if "identity_file" in logDir:
        id = logDir.pop("identity_file")
    for host in logDir:
        name = logDir[host]
        logAgg = "mkdir -p logs && sudo docker logs {} >> logs/{}.txt".format(name, name)
        logCMD = 'ssh {} {} "{}"'.format(id, host, logAgg)
        if debug:
            print(logCMD)
        else:
            os.system(logCMD)
        logCPY = 'mkdir -p logs/logs_{} && scp {} {}:logs/{}.txt logs/logs_{}/{}.txt'.format(host, id, host, name, host, name)
        if debug:
            print(logCPY)
        else:
            os.system(logCPY)
if __name__== "__main__":
  main()
