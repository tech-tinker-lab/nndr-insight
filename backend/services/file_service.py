import glob
import os

def find_files(folder_path, pattern="*.csv"):
    return glob.glob(os.path.join(folder_path, pattern)) 