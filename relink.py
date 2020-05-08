import argparse
from pathlib import Path
import os
import shutil
import time

parser = argparse.ArgumentParser()

parser.add_argument("directory",
                    help="Directory to relink")
parser.add_argument("sourceDir",
                    help="The directory to link from")
args = parser.parse_args()

directory = Path(args.directory)
if directory.name != 'plugins':
    print("The directory name is not 'plugins'. Aborting.")
    exit()
sourceDir = Path(args.sourceDir)
assert directory.is_dir() and sourceDir.is_dir()
tmpDir = directory.parent / "relink{}".format(time.strftime("%Y%m%d%H%M%S"))

# Delete old tmp file
if tmpDir.exists():
    if tmpDir.is_file():
        tmpDir.unlink()
    else:
        os.rmdir(tmpDir)
# Make tmp directory to move directories
os.makedirs(tmpDir)

for file in directory.glob('*'):
    if file.suffix == ".phar" or file == tmpDir:
        continue

    if file.is_dir():
        # Move to a tmp folder
        tmpFile = tmpDir / file.name
        shutil.move(str(file), tmpFile)
    elif file.is_symlink():
        file.unlink()
    else:
        continue

    pharSrcPath = sourceDir / (file.stem + ".phar")
    folderSrcPath = sourceDir / file.stem
    if pharSrcPath.is_file():
        linkFrom = pharSrcPath
    elif folderSrcPath.is_dir():
        linkFrom = folderSrcPath
    else:
        print("Source not found for {}.".format(file.name))
        continue
    os.symlink(os.path.relpath(linkFrom, directory), str(file))

print("Done!")

