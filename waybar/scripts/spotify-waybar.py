#!/usr/bin/env python3

import subprocess

def get_spotify_title():
    try:
        result = subprocess.run(
            ["playerctl", "--player=spotify", "metadata", "title"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )

        title = result.stdout.strip()

        if title:
            return title
        else:
            return "No Music"

    except Exception:
        return "No Music"


if __name__ == "__main__":
    print(get_spotify_title())
