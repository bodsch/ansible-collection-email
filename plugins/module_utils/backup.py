
import os
import shutil
import time


def create_backup(backup: bool = True, file_name: str = "") -> None:
    """
    """
    if backup and os.path.exists(file_name):
        _dir = os.path.dirname(file_name)
        _file = os.path.basename(file_name)
        _datetime = time.strftime("%Y%m%d-%H%M")
        backup_file = os.path.join(_dir, f"{_file}-{_datetime}")
        shutil.copy2(file_name, backup_file)
