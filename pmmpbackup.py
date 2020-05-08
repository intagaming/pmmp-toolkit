"""
Python script to backup PocketMine-MP files
"""
import datetime
import os
import shutil
import time
from pathlib import Path
import argparse
import tarfile

WORK_DIR = str(Path(__file__).parent.absolute()) + '/backups/'
BACKUP_FILES = [
    "players", "plugin_data", "plugins", "PocketMine-MP.phar",
    "resource_packs", "virions", "worlds", "banned-ips.txt",
    "banned-players.txt", "ops.txt", "pocketmine.yml",
    "server.properties", "start.sh", "white-list.txt"
]

# Timing the time to run the script
start_time = time.time()

# Check if backup folder exists
if not Path(WORK_DIR).exists():
    # Create folder
    os.makedirs(WORK_DIR)

print("""
PocketMine-MP Python Backup Script
Running at: {}
Backups will be stored at folder {}
""".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), WORK_DIR))

parser = argparse.ArgumentParser()
parser.add_argument("--path", type=str, action='append', metavar="POCKETMINE_PATH",
                    help="Path to PocketMine-MP folder")
parser.add_argument("-a", action="store_true", dest="archive",
                    help="Archive all the zips to a master zip")
args = parser.parse_args()
folders = []
if args.path is not None:
    folders = [*args.path]


# Validate PocketMine-MP path (roughly)
def validate_path(path):
    path = Path(path)
    return all([
        (path / "start.sh").is_file(),
        (path / "worlds").is_dir(),
        (path / "players").is_dir(),
        (path / "plugins").is_dir(),
        (path / "plugin_data").is_dir(),
    ])


print("Deleting old backups (7 days)")
for file in Path(WORK_DIR).glob("*.tar.gz"):
    creation_time = file.stat().st_ctime
    if (time.time() - creation_time) // 86400 >= 7:
        file.unlink()
        print("Deleted {}".format(file.name))


processed_tarfiles = []
for folder in folders:
    folder_path = Path(folder)

    # Checking...
    if not folder_path.exists():
        print("The folder {} does not exist. Skipping.".format(folder))
        continue
    if not validate_path(folder):
        print("{} is not a valid PMMP path.".format(folder))
        continue

    # Finding new zip name
    tarName = base_tarName = "{}-{}.tar.gz".format(folder_path.name, time.strftime("%Y%m%d-%H%M%S"))
    i = 1  # In case it already existed, for whatever reason
    while Path(WORK_DIR + tarName).exists():
        tarName = base_tarName + "_" + str(i) + ".tar.gz"
        i += 1

    print("Backing up \"{}\":".format(folder))

    # Start compressing
    """
    We compress the players/ and worlds/ directories, as these
    folders are large in size and no. of files. Thus make
    accessing the backup easier and faster.
    """
    players_archive_name = shutil.make_archive(folder_path / "tmp/players", "gztar", folder_path, "players")
    worlds_archive_name = shutil.make_archive(folder_path / "tmp/worlds", "gztar", folder_path, "worlds")

    """
    Okay, now we start archiving the folder, except
    the players/ and worlds/ directories.
    """
    BACKUP_FILES = [filename for filename in BACKUP_FILES if filename not in [
        ".git", "worlds", "players"
    ]]
    with tarfile.open(WORK_DIR + tarName, "w:gz") as tar:
        # Add the 2 previously archived folder
        tar.add(players_archive_name, Path(players_archive_name).name)
        tar.add(worlds_archive_name, Path(worlds_archive_name).name)

        # Add remaining files
        for sub in folder_path.glob("*"):
            if sub.name not in BACKUP_FILES:
                continue
            tar.add(sub, sub.name)

    # Delete tmp folder
    shutil.rmtree(folder_path / "tmp")

    print("Done! Target file: {}".format(tarName))
    processed_tarfiles.append(tarName)


# Summary
if len(processed_tarfiles) > 0:
    print("Successfully backed up {} folders.".format(len(processed_tarfiles)))

if args.archive:
    tarName = "backup-{}.tar.gz".format(time.strftime("%Y%m%d-%H%M%S"))
    with tarfile.open(WORK_DIR + tarName, "w:gz") as tar:
        for file_processed in processed_tarfiles:
            tar.add(WORK_DIR + file_processed, file_processed)
            Path(WORK_DIR + file_processed).unlink()
    print("Successfully archived all the files into {}".format(tarName))

print("All done! Took %.2f seconds." % (time.time() - start_time))
print("\n")
