#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2025, Bodo Schulz <bodo@boone-schulz.de>
# Apache-2.0 (see LICENSE or https://opensource.org/license/apache-2-0)
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import docker
import git
import yaml


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    DEBUG = "\033[1m\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class DiffImageLists:
    """ """

    def __init__(self, local_images, remote_images):
        self.local_images = local_images
        self.remote_images = remote_images

    def parse_image(self, image):
        """
        Gibt ('registry/namespace/image', 'tag') zurück
        """
        if ":" in image:
            name, tag = image.rsplit(":", 1)
        else:
            name, tag = image, "latest"
        return name, tag

    def basename(self, image_name):
        """
        Extracts image name without registry or namespace.
        """
        parts = image_name.split("/")

        return parts[-1]

    def normalize_image_list(self, image_list):
        return dict(self.parse_image(img) for img in image_list)

    def normalize_image_list_with_basename(self, image_list):
        """
        Returns a dict of full_name -> tag and a dict base:tag -> list of full names.
        """
        full_map = {}
        base_map = defaultdict(list)
        for img in image_list:
            name, tag = self.parse_image(img)
            base_id = f"{self.basename(name)}:{tag}"
            full_map[name] = tag
            base_map[base_id].append(name)

        return full_map, base_map

    def image_diff(self):

        local_dict = self.normalize_image_list(self.local_images)
        remote_dict = self.normalize_image_list(self.remote_images)

        output_lines = []
        header = f"{'Image':<40} | {'Local Tag':<15} | {'Remote Tag':<15}"
        output_lines.append(header)
        output_lines.append("=" * len(header))

        all_names = sorted(set(local_dict.keys()) | set(remote_dict.keys()))

        # header = f"{'Image':<40} | {'Local Tag':<15} | {'Remote Tag':<15}"
        # print(header)
        # print("="* len(header))

        for name in all_names:
            local_tag = local_dict.get(name, "")
            remote_tag = remote_dict.get(name, "")
            tag_note = ""

            if local_tag != remote_tag:
                tag_note = (
                    " <-- different"
                    if local_tag and remote_tag
                    else " <-- added/removed"
                )

            output_lines.append(
                f"{name:<40} | {local_tag:<15} | {remote_tag:<15}{tag_note}"
            )

        print("\n".join(output_lines))

    def image_and_registry_diff(self):
        # local_dict = {self.parse_image(img)[0]: self.parse_image(img)[1] for img in self.local_images}
        # remote_dict = {self.parse_image(img)[0]: self.parse_image(img)[1] for img in self.remote_images}

        # Map basenames to full names
        local_by_base = defaultdict(list)
        remote_by_base = defaultdict(list)

        for img in self.local_images:
            name, tag = self.parse_image(img)
            local_by_base[self.basename(name)].append((name, tag))

        for img in self.remote_images:
            name, tag = self.parse_image(img)
            remote_by_base[self.basename(name)].append((name, tag))

        output_lines = []
        header = f"{'Image':<60} | {'Local Tag':<15} | {'Remote Tag':<15} | Note"
        output_lines.append(header)
        output_lines.append("=" * len(header))

        all_basenames = sorted(set(local_by_base.keys()) | set(remote_by_base.keys()))

        for base in all_basenames:
            local_entries = local_by_base.get(base, [])
            remote_entries = remote_by_base.get(base, [])

            matched_local = set()
            matched_remote = set()

            # 1. Match by basename (but registry differs)
            for i, (lname, ltag) in enumerate(local_entries):
                note = None
                if i in matched_local:
                    continue
                for j, (rname, rtag) in enumerate(remote_entries):
                    if j in matched_remote:
                        continue

                    if (lname == rname) and (ltag == rtag):
                        matched_local.add(i)
                        matched_remote.add(j)
                        continue

                    if ltag == rtag:
                        note = "registry change"
                        _reg = f"{lname} ⇄ {rname}"
                        output_lines.append(
                            f"{bcolors.BOLD}{_reg:<60}{bcolors.ENDC} | {ltag:<15} | {rtag:<15} | {note}"
                        )
                    elif (lname != rname) and (ltag != rtag):
                        note = "full update"
                        _reg = f"{lname} ⇄ {rname}"
                        output_lines.append(
                            f"{bcolors.BOLD}{_reg:<60}{bcolors.ENDC} | {ltag:<15} | {bcolors.BOLD}{rtag:<15}{bcolors.ENDC} | {note}"
                        )
                    else:
                        note = "container update"
                        _reg = f"{lname} ⇄ {rname}"
                        output_lines.append(
                            f"{_reg:<60} | {ltag:<15} | {bcolors.BOLD}{rtag:<15}{bcolors.ENDC} | {note}"
                        )

                    matched_local.add(i)
                    matched_remote.add(j)
                    break

            # 3. Unmatched local
            for i, (lname, ltag) in enumerate(local_entries):
                if i not in matched_local:
                    output_lines.append(
                        f"{lname:<60} | {bcolors.BOLD}{ltag:<15}{bcolors.ENDC} | {'':<15} | removed"
                    )

            # 4. Unmatched remote
            for j, (rname, rtag) in enumerate(remote_entries):
                if j not in matched_remote:
                    output_lines.append(
                        f"{rname:<60} | {'':<15} | {bcolors.BOLD}{rtag:<15}{bcolors.ENDC} | added"
                    )

        print("\n".join(output_lines))


class GitHandler:
    """ """

    def __init__(self, clone_path, repo_url, branch, git_user=None, git_token=None):
        """ """
        self.clone_path = clone_path
        self.git_branch = branch
        self.git_repo_url = repo_url
        self.git_token = git_token
        self.git_user = git_user

        print(self.git_repo_url)

        sections = urlparse(self.git_repo_url)
        repo = sections.path.split("/")[-1]
        repo_name = Path(repo).stem

        print(repo_name)

    def _git_remote_url(self):
        parsed_url = urlparse(self.git_repo_url)
        if self.git_user and self.git_token:
            netloc = f"{self.git_user}:{self.git_token}@{parsed_url.hostname}"
            url_with_auth = str(urlunparse(parsed_url._replace(netloc=netloc)))
            return url_with_auth
        else:
            return self.git_repo_url
        # self.logger.debug(f'Git Url with Auth: {url_with_auth}')

    def checkout_target(self):
        """
        Führt ein robustes Checkout durch, egal ob Branch, Tag oder Commit.
        """
        target = self.git_branch

        # Existiert als lokaler Branch
        if target in self.repo.heads:
            print(f"Checkout local branch: {target}")
            self.repo.heads[target].checkout()
            self.repo.remotes.origin.pull(target)

        # Existiert als Remote-Branch
        elif f"origin/{target}" in self.repo.refs:
            print(f"Checkout remote branch: {target}")
            self.repo.git.checkout("-b", target, f"origin/{target}")
            self.repo.remotes.origin.pull(target)

        # Existiert als Tag
        elif target in self.repo.tags:
            print(f"Checkout tag: {target}")
            self.repo.git.checkout(f"tags/{target}")
            print("Note: Detached HEAD state, no pull will be performed.")

        # Vielleicht ein Commit-Hash?
        else:
            try:
                print(f"Trying to checkout commit: {target}")
                self.repo.git.checkout(target)
                print("Note: Detached HEAD state.")
            except Exception:
                print(f"Error: Branch, tag or commit '{target}' not found.")
                sys.exit(1)

        self.last_commit_hash = self.repo.head.commit.hexsha
        print(f"Checked out commit: {self.last_commit_hash}")

    def clone_repo(self):
        """ """
        try:
            if not os.path.exists(f"{self.clone_path}/.git"):
                print(f"Cloning git repo {self.git_repo_url}")
                self.repo = git.Repo.clone_from(self._git_remote_url(), self.clone_path)
            else:
                print("Repo already cloned.")
                self.repo = git.Repo(self.clone_path)

            # Neuer, robuster Checkout
            self.checkout_target()

        except git.GitCommandError as e:
            print(f"Git error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)

        return True

    def clone_git_repo(self):
        """ """
        try:
            if not os.path.exists(f"{self.clone_path}/.git"):
                # print(f"Cloning git repo {self.git_repo_url}")
                self.repo = git.Repo.clone_from(self._git_remote_url(), self.clone_path)
            else:
                print("Repo already cloned, pulling latest changes.")

                try:
                    self.repo = git.Repo(self.clone_path)
                    # print(f"Checking out branch {self.git_branch}")
                    self.repo.git.checkout(self.git_branch)

                    self.repo.remotes.origin.pull()
                except git.GitCommandError as e:
                    print(f"Error pulling updates from git repo: {e}")
                    sys.exit(1)
                except Exception as e:
                    print(f"Error pulling updates from git repo: {e}")
                    sys.exit(1)

        except Exception as e:
            print(f"Error cloning git repo: {e}")
            exit(1)

        self.last_commit_hash = self.repo.head.commit.hexsha
        print(self.last_commit_hash)

        return True

    def show_content(self, content):
        """
        Zeigt den Inhalt einer Datei im aktuell ausgecheckten Zustand (Branch, Tag oder Commit).
        """
        try:
            # HEAD steht für den aktuell ausgecheckten Commit, egal ob Branch, Tag, SHA
            return self.repo.git.show(f"HEAD:{content}")
        except git.GitCommandError as e:
            print(f"Fehler beim Anzeigen des Inhalts von '{content}': {e}")
            return None


class MailcowUpdater:
    """ """

    def __init__(self):
        """ """
        self.args = {}
        self.parse_args()

        self.compose_file = self.args.compose
        self.compose_dir = self.args.compose_dir
        self.update_url = self.args.git_url
        self.update_branch = self.args.branch
        self.dry_run = self.args.dry_run

        if self.compose_file is None and self.compose_dir is None:
            print("please use '--compose' or '--compose-dir'")
            sys.exit(1)

    def parse_args(self):
        """
        parse arguments
        """
        p = argparse.ArgumentParser(description="update mailcow container.")

        p.add_argument(
            "-C", "--compose", required=False, help="compose file", default=None
        )

        # TODO
        # support compose.d directory
        p.add_argument(
            "--compose-dir",
            required=False,
            help="directory with many compose files",
            default=None,
        )

        p.add_argument(
            "-G",
            "--git-url",
            required=False,
            help="git urls for update",
            default="https://github.com/mailcow/mailcow-dockerized.git",
        )

        p.add_argument(
            "-B",
            "--branch",
            required=False,
            help="update againt branch ...",
            default="master",
        )

        p.add_argument(
            "--dry-run",
            required=False,
            help="do nothing.",
            action="store_true",
            default=True,
        )

        self.args = p.parse_args()

    def run(self):
        """ """
        compose_data = None
        if self.compose_dir:
            compose_data = self.read_compose_dir()

        self.compare_images(
            compose_data=compose_data,
            local_file_path=self.compose_file,
            remote_url=self.update_url,
            branch=self.update_branch,
        )

        # if len(added_images) > 0:
        #     if not self.dry_run:
        #         self.pull_new_container(added_images)

    def read_compose_dir(self):
        """ """
        data = dict()
        data["services"] = dict()
        for compose_file in os.listdir(self.compose_dir):
            _file = os.path.join(self.compose_dir, compose_file)
            try:
                with open(_file) as f:
                    d = yaml.safe_load(f)
                    service = d.get("services", None)
                    if service:
                        data["services"].update(service)

            except Exception as e:
                print(f"⚠️ Errors when reading {compose_file}: {e}")

        return data

    def get_images_from_docker_compose_file(self, compose_data, file_path):
        """
        Liest die docker-compose.yml Datei und extrahiert alle Image-Namen.
        """

        if not compose_data:
            with open(file_path, "r") as file:
                docker_compose_content = yaml.safe_load(file)
        else:
            docker_compose_content = compose_data

        # Suche nach allen Image-Referenzen
        images = []
        if isinstance(docker_compose_content, dict):
            images = [
                conf.get("image")
                for service, conf in docker_compose_content.get("services", {}).items()
            ]

        images = sorted(images)

        return images

    def get_images_from_remote_docker_compose(
        self, remote_url=None, repo_path="/tmp/mailcow", branch="master"
    ):
        """ """
        _git = GitHandler(clone_path=repo_path, repo_url=remote_url, branch=branch)
        _git.clone_repo()

        docker_compose_content = _git.show_content("docker-compose.yml")

        if docker_compose_content is None:
            sys.exit(1)

        # Regex für das Extrahieren der "image:"-Zeilen
        images = re.findall(r"image:\s*(\S+)", docker_compose_content)

        images = sorted(images)

        return images

    def pull_new_container(self, images):
        """ """
        client = docker.from_env()

        for image in images:
            try:
                print(f"pull container image: {image}")
                client.images.pull(image)
                # print(f"Erfolgreich: {image}")
            except docker.errors.APIError as e:
                print(f"Error when pulling the image {image}: {str(e)}")

    def side_by_side_diff(self, local_images, remote_images):
        """ """

        def split_image(image):
            if ":" in image:
                name, tag = image.split(":", 1)
            else:
                name, tag = image, "latest"
            return name, tag

        # Indexiere beide Listen nach dem Image-Namen
        local_dict = {split_image(img)[0]: img for img in local_images}
        remote_dict = {split_image(img)[0]: img for img in remote_images}

        all_keys = sorted(set(local_dict.keys()) | set(remote_dict.keys()))

        print("{:<40} | {:<40}".format("Local Images", "Remote Images"))
        print("=" * 85)

        for key in all_keys:
            local = local_dict.get(key, "")
            remote = remote_dict.get(key, "")
            print("{:<40} | {:<40}".format(local, remote))

    def compare_images(self, compose_data, local_file_path, remote_url, branch):
        """
        Vergleicht die Image-Namen der lokalen und der Remote docker-compose.yml.
        """
        local_images = self.get_images_from_docker_compose_file(
            compose_data, local_file_path
        )
        remote_images = self.get_images_from_remote_docker_compose(
            remote_url=remote_url, repo_path="/tmp/mailcow", branch=branch
        )

        diff = DiffImageLists(local_images, remote_images)
        print("")
        diff.image_and_registry_diff()
        print("")

        # # Finden von Unterschieden zwischen den Images
        # local_set = set(local_images)
        # remote_set = set(remote_images)
        #
        # added_images = remote_set - local_set
        # removed_images = local_set - remote_set
        #
        # if added_images or removed_images:
        #     print("Differences in the container images:")
        # else:
        #     print("No differences in the container images.")
        #
        # if added_images:
        #     print("changed images (remote vs. local):")
        #     for image in added_images:
        #         print(f"  - {image}")
        #
        # if removed_images:
        #     print("Removed images (local vs. remote):")
        #     for image in removed_images:
        #         print(f"  - {image}")
        # return (added_images, removed_images)


def main(requirements_file="collections.yml"):
    """ """
    updater = MailcowUpdater()
    updater.run()


if __name__ == "__main__":
    main()
