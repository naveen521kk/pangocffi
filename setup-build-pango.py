import requests
from os import path
import os
import tarfile
import subprocess
import shutil

PANGO_URL = "https://ftp.gnome.org/pub/GNOME/sources/pango/1.47/pango-1.47.0.tar.xz"
build_dir = path.abspath(path.join("build","pango"))
download_dir = path.abspath(path.join("build","download"))
pango_version = "1.47.0"

def shell(cmd, cwd=None):
    """Run a shell command specified by cmd string."""
    call = subprocess.Popen(cmd, shell=True, cwd=cwd,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = call.communicate()
    print(output.decode())
    #if err:
      #raise OSError(err)
if path.exists("build"):
  shutil.rmtree("build")
os.mkdir("build")
os.mkdir("build/pango")
os.mkdir("build/download")
FILE_NAME= path.basename(PANGO_URL)
TAR_FILE=path.join(download_dir,FILE_NAME)
con = requests.get(PANGO_URL)
with open(TAR_FILE,"wb") as f:
  f.write(con.content)
with tarfile.open(TAR_FILE) as f:
    f.extractall(download_dir)
os.rename(path.join(download_dir,f"pango-{pango_version}"), path.join(build_dir))

print("# Upgrade Meson and Ninja")
shell("pip install -U meson ninja")

shell("meson build --default-library=both -Dfontconfig=enabled -Dcairo=enabled -Dfreetype=enabled",cwd=build_dir)
shell("ninja -C build",cwd=build_dir)