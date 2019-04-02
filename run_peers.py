import os
import argparse

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

# Parse argument
parser = argparse.ArgumentParser(description='Read in number of seeders.')
parser.add_argument('-seed', type=boolean, default=True, required=True,
                    help='should these peers seed or download? (default: True)')
parser.add_argument('-num', type=int, nargs='+', default = 3,
                    required=True, help='how many peers should we spin up? (default: 3)')
parser.add_argument('-tor', type=lambda x: is_valid_file(parser, x),
                    required=True, help='What torrent file should we use?')
parser.add_argument('-dest', type=string,required=True,
                    help='What is the name of the file you want to seed/download??')
parser.add_argument('-db', type=boolean, default=False,
                    help='print out commands for debugging? (default: False)')

args = parser.parse_args()
seed, num_seeders, file, file_dest, debug = args[0], args[1], args[2], args[3], args[4]

if seed:
    assert is_valid_file(file_dest)

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
