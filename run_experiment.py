import os
import json
import argparse
import datetime


# Utility Functions
def is_valid_file(parser, file):
    """
    Checks if the file exists, erroring if it doesn't.
    """
    if not os.path.exists(file):
        parser.error("The file %s does not exist!" % file)
    else:
        return file

def copy(file, hosts, dir=False):
    """
    Copies file to hosts, set dir to true if file is a dir
    """
    for host in hosts:
        if dir:
            cpyCMD = "scp -r {} {}:".format(file, host)
        else:
            cpyCMD = "scp {} {}:".format(file, host)
        if debug:
            print(cpyCMD)
        else:
            os.system(cpyCMD)
# Tracker
def tracker(config):
    """
    Creates a tracker according to the configFile
    """
    tracker = "python murder_tracker.py"
    dockerPre = "sudo docker run -d --network host kraken"
    tCMD = 'ssh {} bash "setup.sh; {} {}; clean.sh"'.format(config["tracker_host"], dockerPre ,tracker)
    if debug:
        print(tCMD)
    else:
        os.system(tCMD)

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
    if debug:
        print(gCMD)
    else:
        os.system(gCMD)
    # Create torrent file for it
    dCMD = "python murder_make_torrent.py {}.txt localhost:8998 {}.torrent".format(file, file)
    if debug:
        print(dCMD)
        os.system("touch " + file + ".txt")
        os.system("touch " + file + ".torrent")
    else:
        os.system(dCMD)
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
    time = str(datetime.datetime.now())
    time = time.replace(" ", "_")
    txtfile = file[:-8] + ".txt"
    if seed:
        name = "seed{}".format(str(time))
        cmd = "python btExperiment/run_peers.py -seed -num={} -tor=torrents/{} -dest=torrents/{} -log={}".format(str(config["seeders_per_host"]), file, txtfile, name)
    else:
        name = "peer{}".format(str(time))
        cmd = "python btExperiment/run_peers.py -num={} -tor=torrents/{} -dest=torrents/{} -log={}".format(str(config["leechers_per_host"]), file, txtfile, name)
    if debug:
        cmd = cmd + " -db"
    pCMD = 'ssh {} bash "setup.sh; {}; clean.sh"'.format(host, cmd)
    if debug:
        print(pCMD)
    else:
        os.system(pCMD)
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

# Aggregate logs
def aggLogs(logDir):
    for host in logDir:
        name = logDir[host]
        logAgg = "mkdir -p logs; sudo docker logs {} >> logs/{}.txt;".format(name, name)
        logCMD = 'ssh {} bash "{}"'.format(host, logAgg)
        if debug:
            print(logCMD)
        else:
            os.system(logCMD)
        logCPY = 'mkdir -p logs_{}; scp {}:logs/{}.txt logs_{}/{}.txt'.format(host, host, name, host, name)
        if debug:
            print(logCPY)
        else:
            os.system(logCPY)

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Read in Json Configuration.')
    parser.add_argument('--config', type=str, default="default.json",
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
    if debug: print("Generating logs")
    aggLogs(logDir)

if __name__== "__main__":
  main()
