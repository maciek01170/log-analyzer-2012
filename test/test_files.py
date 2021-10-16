import os
import glob

if __name__ == '__main__':
    folder_path = '../data/'
    for filename in glob.glob(os.path.join(folder_path, '*.log')):
        with open(filename, 'r') as f:
            lines = f.readlines()
            print(f"{filename}: {len(lines)} lines")
