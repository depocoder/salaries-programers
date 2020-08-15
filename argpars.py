import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('integers', metavar='N', type=str, nargs='*', default=['1'],
                    help='an integer for the accumulator')

args = parser.parse_args()
print(args.integers)