import time, os, urllib
from urllib.request import urlopen
from pathlib import Path

max_attempts = 80
attempts = 0
sleeptime = 10  # in seconds, no reason to continuously try if network is down


def download(url, destinationPath):
    global attempts
    global max_attempts
    global sleeptime
    while attempts < max_attempts:
        time.sleep(sleeptime)
        try:
            response = urlopen(url, timeout=5)
            content = response.read()
            f = open(destinationPath, "wb")
            f.write(content)
            f.close()
            break
        except urllib.error.URLError as e:
            attempts += 1
            print(str(e))


globalPath = os.path.join("FALdetector", "weights", "global.pth")
localPath = os.path.join("FALdetector", "weights", "local.pth")
globalURL = "https://www.dropbox.com/s/rb8zpvrbxbbutxc/global.pth?dl=1"
localURL = "https://www.dropbox.com/s/pby9dhpr6cqziyl/local.pth?dl=1"
if not os.path.isfile(globalPath):
    download(globalURL, globalPath)
if not os.path.isfile(localPath):
    download(localURL, localPath)
