# installer.py
import os
import subprocess
import sys
import platform
import shutil

def install_pyinstaller():
    """Install PyInstaller if it is not already installed."""
    print("Installing PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully")
        return True
    except Exception as e:
        print(f"Error installing PyInstaller: {str(e)}")
        return False

def build_executables():
    """Build standalone executables for the server and client."""
    if not shutil.which("pyinstaller"):
        if not install_pyinstaller():
            print("Cannot continue without PyInstaller")
            return False

    print("\nBuilding client executable...")
    client_options = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "LinkOpener-Client",
        "client.py"
    ]

    print("\nBuilding server executable...")
    server_options = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "LinkOpener-Server",
        "server.py"
    ]

    try:
        subprocess.check_call(client_options)
        subprocess.check_call(server_options)

        # Copy the executables to the current directory
        if platform.system() == "Windows":
            shutil.copy("dist/LinkOpener-Client.exe", ".")
            shutil.copy("dist/LinkOpener-Server.exe", ".")
        else:
            shutil.copy("dist/LinkOpener-Client", ".")
            shutil.copy("dist/LinkOpener-Server", ".")

        print("\nBuild complete! Executables are in the current directory.")
        return True
    except Exception as e:
        print(f"Error building executables: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Remote Link Opener Installer ===")
    print("This script will create executable files for the Remote Link Opener system")

    input("Press Enter to continue...")
    build_executables()