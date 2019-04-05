import os
import argparse

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

# Parse argument
parser = argparse.ArgumentParser(description='Read in number of seeders.')
parser.add_argument('-seed', action='store_true',
                    help='should these peers seed or download? (default: True)')
parser.add_argument('-num', type=int, default = 3,
                    required=True, help='how many peers should we spin up? (default: 3)')
parser.add_argument('-tor', type=lambda x: is_valid_file(parser, x),
                    required=True, help='What torrent file should we use?')
parser.add_argument('-dest',required=True,
                    help='What is the name of the file you want to seed/download??')
parser.add_argument('-db', action='store_true', default=False,
                    help='print out commands for debugging? (default: False)')

args = parser.parse_args()
seed, num_seeders, file, file_dest, db = args.seed, args.num, args.tor, args.dest, args.db

if seed:
    assert is_valid_file(parser, file_dest), "Seeders require the file: " + file_dest
else:
    os.system("rm " + file_dest)

# Create peers
for i in range(num_seeders):
    if seed:
        name = "seed" + str(i)
    else:
        name = "peer" + str(i)
    dockerPre = ["sudo docker run --name", name, "-d --network host kraken"]
    murderClient = ["python murder_client.py seed", file, file_dest, "localhost"]
    CMD = " ".join(dockerPre + murderClient)
    if db:
        print(CMD)
    else:
        os.system(CMD)
