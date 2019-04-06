import os
import json
import argparse

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

# Parse argument
parser = argparse.ArgumentParser(description='Read in Json Configuration.')
parser.add_argument('--config', type=str, default="default.json",
                    help='Pass in a JSON detailing how to run experiment')
parser.add_argument('-db', action='store_true',
                    help='prints out commands instead of executing to debug')
args = parser.parse_args()
configFile, debug = args.config, args.db

# Parse argument JSON
with open(configFile) as f:
    config = json.load(f)
print(config)

# Docker prefix for all commands
dockerPre = ["sudo docker run -d --network host kraken"]

# Copy setup.sh to all the hosts
hosts = [config["tracker_host"]] + config["seeder_hosts"] + config["leecher_hosts"]
for host in hosts:
    cpyCMD = "scp setup.sh " + host + ":"
    if debug:
        print(cpyCMD)
    else:
        os.system(cpyCMD)
# Start tracker
# SSH into host?
tracker = ["python murder_tracker.py"]
tCMD = " ".join(["ssh", config["tracker_host"], "bash setup.sh;"] + dockerPre + tracker)
if debug:
    print(tCMD)
else:
    os.system(tCMD)

# Make all required torrents
def genTorrent(size):
    """ Creates a torrent of that size named t_file_size.torrent"""
    # Generate file of appropriate size
    fillStr = '"y"'
    if size % 8 == 0:
        fillStr = 'Net Sys'
    file = "torrents/test_" + str(size)
    repettions = str(size // (len(fillStr) + 1))
    gCMD = " ".join(["yes", fillStr, "| head -n",  repettions, ">", file + ".txt"])
    if debug:
        print(gCMD)
    else:
        os.system(gCMD)
    # Create torrent file for it
    murderTorr = ["python murder_make_torrent.py", file + ".txt", "localhost", file + ".torrent"]
    dCMD = " ".join(murderTorr)
    if debug:
        print(dCMD)
        os.system("touch " + file + ".txt")
        os.system("touch " + file + ".torrent")
    else:
        os.system(dCMD)
    return file

if not os.path.isdir("torrents"):
    os.system("mkdir torrents")
for i in config["torrent_sizes"]:
    genTorrent(i)
# Create seeders
def gen_peer(host, file, seed=False):
    txtfile = file[:-8] + ".txt"
    if seed:
        cmd = ["python run_peers.py -seed -num=" + str(config["seeders_per_host"]), "-tor=torrents/" + file, "-dest=torrents/" + txtfile]
    else:
        cmd = ["python run_peers.py -num=" + str(config["leechers_per_host"]), "-tor=torrents/" + file, "-dest=torrents/" + txtfile]
    if db:
        cmd = cmd + [" -db"]
    pCMD = " ".join(["ssh", host, "bash setup.sh;"] + cmd)
    if debug:
        print(pCMD)
    else:
        os.system(pCMD)

for host in config["seeder_hosts"]:
    for file in os.listdir("torrents"):
        if file.endswith(".torrent"):
            gen_peer(host, file, True)
# Create leechers
for host in config["leecher_hosts"]:
    for file in os.listdir("torrents"):
        if file.endswith(".torrent"):
            gen_peer(host, file)
# Aggreagate logs
