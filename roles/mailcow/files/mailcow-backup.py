#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2025, Bodo Schulz <bodo@boone-schulz.de>
# Apache-2.0 (see LICENSE or https://opensource.org/license/apache-2-0)
# SPDX-License-Identifier: Apache-2.0


import os
import time
import yaml
import docker
import logging
import argparse


class ContainerVolumeBackup():
    """
    """

    def __init__(self):
        """
        """
        self.args = {}
        self.parse_args()

        self.compose_file = self.args.compose_file
        self.backup_directory = self.args.backup_directory

        self.datetime_readable = time.strftime("%Y-%m-%d")

    def parse_args(self):
        """
            parse arguments
        """
        p = argparse.ArgumentParser(
            description='create docker volume backups.')

        p.add_argument(
            "-c",
            "--compose-file",
            required=False,
            help="bdocker compose file to parse volume definitions",
            default=f"{os.getcwd()}/docker-compose.yml"
        )

        p.add_argument(
            "-d",
            "--backup-directory",
            required=False,
            help="backup directory to store",
            default=os.getcwd()
        )

        self.args = p.parse_args()

    def run(self):
        """
        """
        logging.basicConfig(level=logging.INFO)
        relevant_volumes = self.get_relevant_volumes(self.compose_file)

        if relevant_volumes:
            self.backup_volumes(relevant_volumes, self.backup_directory)
            print("Backup abgeschlossen.")
        else:
            print("Keine relevanten Volumes gefunden.")

    def get_defined_volumes(self, compose_path):
        """Liest die definierten Volumes aus der Mailcow-Compose-Konfiguration."""
        volumes = set()

        # Prüfen, ob die Compose-Datei existiert
        if not os.path.exists(compose_path):
            logging.error(f"Die Datei {compose_path} wurde nicht gefunden!")
            return volumes

        try:
            with open(compose_path, "r") as file:
                compose_data = yaml.safe_load(file)
                if "volumes" in compose_data:
                    volumes = set(compose_data["volumes"].keys())
        except Exception as e:
            logging.error(f"Fehler beim Einlesen der {compose_path}: {e}")

        return volumes

    def get_existing_volumes(self):
        """Ermittelt die tatsächlich in Docker vorhandenen Volumes."""
        client = docker.from_env()
        return {vol.name for vol in client.volumes.list()}

    def get_relevant_volumes(self, compose_path):
        """Vergleicht definierte und existierende Volumes und gibt nur die relevanten zurück."""
        defined_volumes = self.get_defined_volumes(compose_path)
        existing_volumes = self.get_existing_volumes()

        relevant_volumes = defined_volumes.intersection(existing_volumes)

        logging.info(f"Gefundene und vorhandene Volumes: {relevant_volumes}")
        return relevant_volumes

    def backup_volumes(self, volumes, backup_dir):
        """Erstellt ein Backup der angegebenen Docker-Volumes."""
        client = docker.from_env()
        os.makedirs(backup_dir, exist_ok=True)

        for volume in volumes:
            backup_file = os.path.join(backup_dir, f"{volume}.tar.gz")
            container = client.containers.create(
                image="mailcow/backup:latest",
                command=f"/bin/tar --warning='no-file-ignored' --use-compress-program="pigz --rsyncable -p 1" -Pcvpf /backup/backup_{volume}.tar.gz /{volume}",
                volumes={
                    "/backup": {
                        f"{self.backup_directory}/mailcow-{self.datetime_readable}":
                        "mode": "rw"
                    },
                    volume: {
                        'bind': f"/{volume}",
                        'mode': 'ro'
                    }
                },
                name=f"backup_{volume}",
                detach=True
            )
            container.start()

            with open(backup_file, 'wb') as f:
                bits, _ = container.get_archive('/data')
                for chunk in bits:
                    f.write(chunk)

            container.stop()
            container.remove()
            logging.info(
                f"Backup für Volume '{volume}' erfolgreich erstellt: {backup_file}")


if __name__ == "__main__":
    """
    """
    r = ContainerVolumeBackup()

    r.run()
