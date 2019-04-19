import os
import argparse
from utils import is_valid_file

def main():
    # Create peers
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
    parser.add_argument('-log',required=True,
                            help='What should we name the logFile?')
    parser.add_argument('-db', action='store_true', default=False,
                        help='print out commands for debugging? (default: False)')
    parser.add_argument("-u_rate", type=int, help="Upload rate in kb/s")
    parser.add_argument("-d_rate", type=int, help="Download rate in kb/s")

    args = parser.parse_args()
    seed, num_seeders, file = args.seed, args.num, args.tor
    file_dest, log, debug = args.dest, args.log, args.db
    u_rate, d_rate = args.u_rate, args.d_rate

    if seed:
        assert is_valid_file(parser, file_dest), "Seeders require the file: " + file_dest
    else:
        os.system("rm " + file_dest)

    for i in range(num_seeders):
        dockerPre = "sudo docker run -d --name {} --network host kraken".format(log)
        murderClient = "python murder_client.py"
        args = "--ip localhost --responsefile {} --saveas {} --upload_rate {} --download_rate {}".format(file, file_dest, u_rate, d_rate)
        CMD = "{} {} {}".format(dockerPre, murderClient, args)
        if debug:
            print(CMD)
        else:
            os.system(CMD)

if __name__== "__main__":
  main()
