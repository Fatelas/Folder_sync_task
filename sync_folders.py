import os
import sys
import shutil
import time
import hashlib

def hash_file(file_path):
    """Calculate the MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def sync_folders(source_folder, replica_folder, log_file):
    """Synchronize source folder to replica folder."""

    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] Starting synchronization\n')
    with open(log_file, 'a') as log:
        for root, dirs, files in os.walk(source_folder):
            for dir in dirs:
                source_dir_path = os.path.join(root, dir)
                replica_dir_path = os.path.join(replica_folder, os.path.relpath(source_dir_path, source_folder))

                if not os.path.exists(replica_dir_path):
                    message = f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] Copying directory {source_dir_path} to {replica_dir_path}\n'
                    print(message)  # Print to console
                    log.write(message)  # Write to log file
                    shutil.copytree(source_dir_path, replica_dir_path)

            for file in files:
                source_file_path = os.path.join(root, file)
                replica_file_path = os.path.join(replica_folder, os.path.relpath(source_file_path, source_folder))

                if os.path.exists(replica_file_path):
                    if hash_file(source_file_path) != hash_file(replica_file_path):
                        operation = f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] Updating {replica_file_path}\n'
                        print(operation)
                        log.write(operation)
                        shutil.copy2(source_file_path, replica_file_path)
                else:
                    operation = f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] Copying {source_file_path} to {replica_file_path}\n'
                    print(operation)
                    log.write(operation)
                    shutil.copy2(source_file_path, replica_file_path)

        for root, dirs, files in os.walk(replica_folder):
            for dir in dirs:
                replica_dir_path = os.path.join(root, dir)
                source_dir_path = os.path.join(source_folder, os.path.relpath(replica_dir_path, replica_folder))

                # If the directory doesn't exist in the source folder, delete it
                if not os.path.exists(source_dir_path):
                    message = f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] Deleting directory {replica_dir_path}\n'
                    print(message)  # Print to console
                    log.write(message)  # Write to log file
                    shutil.rmtree(replica_dir_path)

            for file in files:
                replica_file_path = os.path.join(root, file)
                source_file_path = os.path.join(source_folder, os.path.relpath(replica_file_path, replica_folder))

                if not os.path.exists(source_file_path):
                    operation = f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] Deleting {replica_file_path}\n'
                    print(operation)
                    log.write(operation)
                    os.remove(replica_file_path)

    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] Synchronization completed\n')

def main():
    if len(sys.argv) != 5:
        print("how to run: python sync_folders.py source_folder replica_folder interval_sec log_file")
        sys.exit(1)

    source_folder = sys.argv[1]
    replica_folder = sys.argv[2]
    sync_interval = int(sys.argv[3])
    log_file = sys.argv[4]

    while True:
        sync_folders(source_folder, replica_folder, log_file)
        time.sleep(sync_interval)

if __name__ == "__main__":
    main()
