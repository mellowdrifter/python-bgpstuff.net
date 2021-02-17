import bgpstuff
import argparse

client = bgpstuff.Client()

def get_cli_args():
    parser = argparse.ArgumentParser(description="A CLI Tool for BGPStuff.net")
    parser.add_argument(
        '--totals', 
        action="store_true",
        help='')

    args = parser.parse_args()

    return args

def print_totals():
    total_v4 = client.get_totals()
    total_v6 = client.get_totals()
    print(f"{client.total_v4} IPv4 Routes")
    print(f"{client.total_v6} IPv6 Routes")

def cli():
    args = get_cli_args()

    if args.totals:
        print_totals()
    else:
        print("Please Provide an Argument")
