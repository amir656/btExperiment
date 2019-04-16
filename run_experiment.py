import os
import json
import argparse
import time
import json
import threading
from utils import is_valid_file

def execThread(cmd):
    def sleep_and_print(cmd):
        time.sleep(1)
        print(cmd)
    if debug:
        c = lambda : sleep_and_print(cmd)
    else:
        c = lambda : os.system(cmd)
    t = threading.Thread(target=c)
    t.dameon = True
    t.start()

def copy(file, hosts, dir=False):
    """
    Copies file to hosts, set dir to true if file is a dir
    """
    for host in hosts:
        if dir:
            cpyCMD = "scp -r {} {}:".format(file, host)
        else:
            cpyCMD = "scp {} {}:".format(file, host)
        execThread(cpyCMD)
# Tracker
def tracker(config):
    """
    Creates a tracker according to the configFile
    """
    tracker = "python murder_tracker.py"
    dockerPre = "sudo docker run -d --network host kraken"
    tCMD = 'ssh {} bash "setup.sh; {} {}; clean.sh"'.format(config["tracker_host"], dockerPre ,tracker)
    execThread(tCMD)

# Torrents
def genTorrent(size):
    """ Creates a torrent of size `size` named test_`size`.torrent"""
    # Generate file of appropriate size
    fillStr = '"y"'
    if size % 8 == 0:
        fillStr = '"Net Sys"'
    file = "torrents/test_" + str(size)
    repettions = str(size // (len(fillStr) - 1))
    gCMD = "yes {} | head -n {} > {}.txt".format(fillStr, repettions, file)
    execThread(gCMD)
    # Create torrent file for it
    dCMD = "python murder_make_torrent.py {}.txt localhost:8998 {}.torrent".format(file, file)
    execThread(dCMD)
    os.system("touch " + file + ".txt")
    os.system("touch " + file + ".torrent")
    return file

def genTorrents(config):
    """
    Creates torrents according to the config file.
    """
    if not os.path.isdir("torrents"):
        os.system("mkdir torrents")
    for i in config["torrent_sizes"]:
        genTorrent(i)

# Peers
def gen_peer(host, file, config, seed=False):
    """
    Generates a command to create leechers or seeders of the `file` on the `host`.
    Command returns a list of the names of the created docker containers for logs.
    """
    date = str(int(time.time()))
    date = date.replace(" ", "_")
    txtfile = file[:-8] + ".txt"
    if seed:
        name = "seed{}".format(str(date))
        cmd = "python btExperiment/run_peers.py -seed -num={} -tor=torrents/{} -dest=torrents/{} -log={}".format(str(config["seeders_per_host"]), file, txtfile, name)
    else:
        name = "peer{}".format(str(date))
        cmd = "python btExperiment/run_peers.py -num={} -tor=torrents/{} -dest=torrents/{} -log={}".format(str(config["leechers_per_host"]), file, txtfile, name)
    if debug:
        cmd = cmd + " -db"
    pCMD = 'ssh {} bash "setup.sh; {}; clean.sh"'.format(host, cmd)
    execThread(pCMD)
    return name

def gen_peers(config, logDir):
    # Create seeders
    for host in config["seeder_hosts"]:
        for file in os.listdir("torrents"):
            if file.endswith(".torrent"):
                logDir[host] = gen_peer(host, file, config, True)
    # Create leechers
    for host in config["leecher_hosts"]:
        for file in os.listdir("torrents"):
            if file.endswith(".torrent"):
                logDir[host] = gen_peer(host, file, config)

def saveLogs(logDir):
    date = str(int(time.time()))
    date = date.replace(" ", "_")
    j = json.dumps(logDir)
    os.system("mkdir -p log_locations")
    f = open("log_locations/logs{}.json".format(date),"w")
    f.write(j)
    f.close()

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Read in Json Configuration.')
    parser.add_argument('--config', type=lambda x: is_valid_file(parser, x), default="default.json",
                        help='Pass in a JSON detailing how to run experiment')
    parser.add_argument('-db', action='store_true',
                        help='prints out commands instead of executing to debug')
    args = parser.parse_args()
    global debug
    configFile, debug = args.config, args.db

    # Parse argument JSON
    with open(configFile) as f:
        config = json.load(f)
    if debug:
        print(config)

    # List of all hosts
    hosts = [config["tracker_host"]] + config["seeder_hosts"] + config["leecher_hosts"]
    # Copy setup.sh and clean.sh to all the hosts
    copy('setup.sh', hosts)
    copy('clean.sh', hosts)
    # Start tracker
    if debug: print("Generating tracker")
    tracker(config)
    # Generate torrents
    if debug: print("Generating torrents")
    genTorrents(config)
    # Copy torrents to all the hosts
    copy('torrents', hosts[1:], dir=True)
    # Build docker image with torrents inside
    if not debug:
        os.system('sudo docker build -t kraken .')
    if debug: print("Generating peers")
    logDir = {}
    gen_peers(config, logDir)
    if debug: print("Saving logs")
    saveLogs(logDir)

if __name__== "__main__":
  main()
