import sys
from pas import pas

def main():
    pas('input-seed-2-size-1000.json', '1', 30)
    exit()
    if len(sys.argv) != 4:
        print("[Warning] You must pass three and only three parameters for the program to run, the first is the input file, the second is the random seed and the third is the max time for lahc mono")

    if sys.argv[1].split('.')[1] != 'json':
        print(f"[Error] The input file must be a '.json' file, the argument has extension '.{sys.argv[1].split('.')[1]}'")

    pas(sys.argv[1], sys.argv[2], sys.argv[3])
    # pas('instance.json')

if __name__ == "__main__":
    main()