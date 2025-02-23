#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2025, Bodo Schulz <bodo@boone-schulz.de>
# Apache-2.0 (see LICENSE or https://opensource.org/license/apache-2-0)
# SPDX-License-Identifier: Apache-2.0

import os
import re
import requests

def get_registry_and_image(image_name):
    if "/" in image_name and not image_name.startswith("library/"):
        registry, image = image_name.split("/", 1)
        if "." in registry or ":" in registry:  # Custom registry detected
            return registry, image
    return "registry.hub.docker.com", image_name  # Default to Docker Hub

def get_latest_tag(image_name, registry, current_tag):
    if registry == "registry.hub.docker.com":
        url = f"https://registry.hub.docker.com/v2/repositories/{image_name}/tags/"
    else:
        url = f"https://{registry}/v2/{image_name}/tags/list"

    response = requests.get(url)
    if response.status_code == 200:
        if registry == "registry.hub.docker.com":
            tags = response.json().get("results", [])
            filtered_tags = [tag["name"] for tag in tags if not re.search(r"snapshot|nightly|dev", tag["name"], re.IGNORECASE)]
            if current_tag == "latest" or not re.match(r"^\d+", current_tag):
                return current_tag  # Behalte latest oder nicht-numerische Tags
            numeric_tags = [t for t in filtered_tags if re.match(r"^\d+(\.\d+)*(-\w+)?$", t)]
            if numeric_tags:
                return sorted(numeric_tags, key=lambda v: list(map(int, re.findall(r"\d+", v))), reverse=True)[0]
        else:
            filtered_tags = [tag for tag in response.json().get("tags", []) if not re.search(r"snapshot|nightly|dev", tag, re.IGNORECASE)]
            if current_tag == "latest" or not re.match(r"^\d+", current_tag):
                return current_tag  # Behalte latest oder nicht-numerische Tags
            numeric_tags = [t for t in filtered_tags if re.match(r"^\d+(\.\d+)*(-\w+)?$", t)]
            if numeric_tags:
                return sorted(numeric_tags, key=lambda v: list(map(int, re.findall(r"\d+", v))), reverse=True)[0]
    return current_tag

def parse_docker_images(directory):
    image_pattern = re.compile(r"image:\s*(\S+)")

    if not os.path.isdir(directory):
        print(f"Verzeichnis {directory} existiert nicht.")
        return

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        if not os.path.isfile(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                match = image_pattern.search(line)
                if match:
                    image = match.group(1)
                    registry, image_name = get_registry_and_image(image)
                    image_name, tag = (image_name.split(":", 1) if ":" in image_name else (image_name, "latest"))
                    latest_tag = get_latest_tag(image_name, registry, tag)
                    update_available = latest_tag != tag
                    print(f"Datei: {filename} -> Registry: {registry}, Image: {image_name}, Aktuelle Version: {tag}, Neueste Version: {latest_tag}, Update verfügbar: {update_available}")

if __name__ == "__main__":
    parse_docker_images("docker-compose.d")
