import os
import json
import argparse
import time
import json
import threading
import random
import re
from utils import is_valid_file, wait

def execThread(cmd):
    def sleep_and_print(t, cmd):
        time.sleep(t)
        print(cmd)
    if debug:
        c = lambda : sleep_and_print(1, cmd)
    else:
        c = lambda : os.system(cmd)
    t = threading.Thread(target=c)
    t.dameon = True
    t.start()
    workers.append(t)
    return t

def copy(file, hosts, dir=False):
    """
    Copies file to hosts, set dir to true if file is a dir
    """
    for host in hosts:
        r, i = '', ''
        if dir:
            r = "-r"
        cpyCMD = "scp {} {} {} {}:".format(id, r, file, host)
        execThread(cpyCMD)

def runAllHosts(file, hosts, supress=False):
    threads = []
    for host in hosts:
        cpyCMD = "scp {} {} {}:".format(id, file, host)
        runCMD = "ssh {} {} bash {}".format(id, host, file)
        if supress:
            runCMD = runCMD + " > /dev/null"
        execThread("{} && {}".format(cpyCMD, runCMD))

# Tracker
def tracker(config):
    """
    Creates a tracker according to the configFile
    """
    tracker = "python murder_tracker.py"
    dockerPre = "sudo docker run -d --network host kraken"
    tCMD = 'ssh {} {} {} {};'.format(id, config["tracker_host"], dockerPre ,tracker)
    execThread(tCMD)

# Torrents
def genTorrent(size, tracker_host):
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
    dCMD = "python murder_make_torrent.py {}.txt {}:8998 {}.torrent".format(file, tracker_host, file)
    execThread(dCMD)
    if debug:
        os.system("touch " + file + ".txt")
        os.system("touch " + file + ".torrent")
    return file

def genTorrents(config):
    """
    Creates torrents according to the config file.
    """
    os.system("mkdir -p torrents")
    for i in config["torrent_sizes"]:
        genTorrent(i, config["tracker_host"])

# Peers
def gen_peer(host, file, config, seed=False):
    """
    Generates a command to create leechers or seeders of the `file` on the `host`.
    Command returns a list of the names of the created docker containers for logs.
    """
    # Appease docker's naming scheme by making time a number without a decimal
    date = str(int(time.time()*1000000 + random.randint(1, 100)))
    txtfile = file[:-8] + ".txt"
    size = re.match(r"test_(\d+)\.torrent", file).group(1)
    if seed:
        name = "{}-seed{} -seed".format(size, date)
    else:
        name = "{}-peer{}".format(size, date)
    cmd = '"cd $(cat dir.txt); python btExperiment/run_peers.py -num={} -tor=torrents/{} -dest=torrents/{} -log={} -u_rate={} -d_rate={}"'.format(str(config["leechers_per_host"]), file, txtfile, name, config["upload_rate"], config["download_rate"])
    if debug:
        cmd = cmd + " -db"
    pCMD = 'ssh {} {} {}'.format(id, host, cmd)
    execThread(pCMD)
    return name.strip(" -seed")

def gen_peers(config, logDir):
    # Create seeders
    for host in config["seeder_hosts"]:
        for file in os.listdir("torrents"):
            if file.endswith(".torrent"):
                logDir[host].append(gen_peer(host, file, config, True))
    # Create leechers
    for host in config["leecher_hosts"]:
        for file in os.listdir("torrents"):
            if file.endswith(".torrent"):
                logDir[host].append(gen_peer(host, file, config))

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
    parser.add_argument('-shutdown', action='store_true',
                        help='shuts down all docker containers on hosts in config. Only flag after experiment is finished. Will shutdown all docker containers on the host, not just ones run in experiments.')
    args = parser.parse_args()
    global debug
    global workers
    configFile, debug = args.config, args.db
    workers = []
    # Parse argument JSON
    with open(configFile) as f:
        config = json.load(f)
    if debug: print(config)

    global id
    id = ''
    if config["identity_file"]:
        id = "-i {}".format(config["identity_file"])

    # List of all hosts
    hosts = [config["tracker_host"]] + config["seeder_hosts"] + config["leecher_hosts"]
    if args.shutdown:
        runAllHosts("shutdown.sh", hosts, supress=True)
        return
    # Copy setup.sh and run it. Waits for all of them to finish before proceeding.
    runAllHosts("setup.sh", hosts, supress=True)
    wait(workers)
    # Generate torrents
    if debug: print("Generating torrents")
    genTorrents(config)
    # Start tracker
    if debug: print("Generating tracker")
    tracker(config)
    # Copy torrents to all the hosts
    copy('torrents', hosts[1:], dir=True)

    if debug: print("Generating peers")
    logDir = {host:[] for host in hosts}
    gen_peers(config, logDir)
    if debug: print("Saving logs")
    if id:
        logDir["identity_file"] = id
    saveLogs(logDir)
    if debug: print("{} workers".format(len(workers)))
    # Waits on all threads to finish before cleaning
    wait(workers)
    runAllHosts("clean.sh", hosts)

if __name__== "__main__":
  main()
