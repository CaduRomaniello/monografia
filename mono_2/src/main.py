import sys
from pas import pas

def main():
    # pas('input-seed-6-size-1000.json', '1', 120, "nsgaII")
    # exit()
    if len(sys.argv) != 5:
        print("[Warning] You must pass four and only four parameters for the program to run, the first is the input file, the second is the random seed, the third is the max time for lahc mono and the fourth is the algorithm")

    if sys.argv[1].split('.')[1] != 'json':
        print(f"[Error] The input file must be a '.json' file, the argument has extension '.{sys.argv[1].split('.')[1]}'")

    algorithms = ["lahc-mono", "lahc-multi", "nsgaII"]
    if sys.argv[4] not in algorithms:
        print(f"[Error] The algorithm must be one of the following: {algorithms}")

    pas(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

if __name__ == "__main__":
    main()