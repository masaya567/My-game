import os
import requests

VERSION_URL = "https://raw.githubusercontent.com/masaya567/My-game/main/version.txt"
EXE_URL = "https://github.com/masaya567/My-game/releases/latest/download/PianoTiles.zip"


LOCAL_VERSION_PATH = os.path.join("data", "version.txt")
LOCAL_EXE_PATH = os.path.join("PianoTiles.exe")


def get_local_version():
    if not os.path.exists(LOCAL_VERSION_PATH):
        return "0.0.0"
    with open(LOCAL_VERSION_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def get_remote_version():
    try:
        r = requests.get(VERSION_URL, timeout=3)
        if r.status_code == 200:
            return r.text.strip()
    except:
        return None
    return None


def is_newer(remote, local):
    return tuple(map(int, remote.split("."))) > tuple(map(int, local.split(".")))


def download_new_version():
    r = requests.get(EXE_URL, stream=True)
    if r.status_code != 200:
        return False

    with open("PianoTiles_new.exe", "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    os.replace("PianoTiles_new.exe", LOCAL_EXE_PATH)
    return True


def check_update():
    local = get_local_version()
    remote = get_remote_version()

    if remote is None:
        return False, "ネットワークエラー"

    if is_newer(remote, local):
        return True, remote

    return False, None
