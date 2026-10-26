import os
import shutil
import time


def create_backup(backup: bool = True, file_name: str = "") -> None:
    """
    rename file
        master.cf -> master_backup-20261026-0806.cf
    """
    if backup and os.path.exists(file_name):
        _dir = os.path.dirname(file_name)
        _file = os.path.basename(file_name)
        filename, file_extension = os.path.splitext(_file)
        _datetime = time.strftime("%Y%m%d-%H%M")
        _file_name = f"{filename}_backup-{_datetime}{file_extension}"
        backup_file = os.path.join(_dir, _file_name)

        shutil.copy2(file_name, backup_file)
