import sys
from pas import pas

def main():
    # if len(sys.argv) != 2:
    #     print("[Warning] You must pass one and only one parameter for the input file name")

    # if sys.argv[1].split('.')[1] != 'json':
    #     print(f"[Error] The input file must be a '.json' file, the argument has extension '.{sys.argv[1].split('.')[1]}'")

    # pas(sys.argv[1])
    pas('instance.json')

if __name__ == "__main__":
    main()