import requests
import os
import sys
import subprocess
import win32com.client

RED = '\033[91m'
BLUE = '\033[94m'
GREEN = '\033[92m'
RESET = '\033[0m'

class AppUpdater:
    def __init__(self, repo_owner, repo_name, current_version):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        self.github_api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        self.executable_name = "pesquisa.exe"

    def get_latest_release_info(self):
        """Fetches the latest release information from GitHub."""
        try:
            response = requests.get(self.github_api_url)
            response.raise_for_status() # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"{RED}Error fetching latest release info: {e}{RESET}")
            return None

    def is_new_version_available(self, latest_release):
        """Compares the current version with the latest release version."""
        if not latest_release:
            return False

        latest_tag_name = latest_release.get("tag_name")
        if not latest_tag_name:
            return False

        # Assuming tag_name is in format "vX.Y.Z" or "vN"
        latest_version_str = latest_tag_name.lstrip('v')
        current_version_str = str(self.current_version).lstrip('v')

        # Simple version comparison (e.g., "1" < "2", "1.0" < "1.1")
        # For more robust comparison, consider packaging.version.parse
        try:
            # Convert to integers for comparison if they are simple numbers
            if latest_version_str.isdigit() and current_version_str.isdigit():
                return int(latest_version_str) > int(current_version_str)
            
            # Otherwise, do a string comparison (might not be perfect for all versioning schemes)
            return latest_version_str > current_version_str
        except ValueError:
            # Fallback to string comparison if conversion to int fails
            return latest_version_str > current_version_str


    def download_new_version(self, latest_release):
        """Downloads the new executable from the latest release assets."""
        assets = latest_release.get("assets", [])
        download_url = None
        for asset in assets:
            if asset.get("name") == self.executable_name:
                download_url = asset.get("browser_download_url")
                break

        if not download_url:
            print(f"{RED}Executable '{self.executable_name}' not found in the latest release assets.{RESET}")
            return False

        try:
            print(f"{BLUE}Downloading new version from: {download_url}{RESET}")
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            # Save the downloaded file to a temporary location
            temp_exe_path = os.path.join(os.path.dirname(sys.executable), f"new_{self.executable_name}")
            with open(temp_exe_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"{GREEN}Downloaded new version to: {temp_exe_path}{RESET}")
            return temp_exe_path
        except requests.exceptions.RequestException as e:
            print(f"{RED}Error downloading new version: {e}{RESET}")
            return None

    def update_application(self, temp_exe_path):
        """Initiates the application update and restart process."""
        current_exe_path = sys.executable
        self._restart_application(current_exe_path, temp_exe_path)
        return True

    def check_for_updates(self):
        """Checks for updates and performs the update if a new version is available."""
        current_exe_path = sys.executable # Define current_exe_path here
        print(f"{BLUE}Checking for updates...{RESET}")
        latest_release = self.get_latest_release_info()
        if latest_release and self.is_new_version_available(latest_release):
            latest_tag_name = latest_release.get("tag_name", "N/A")
            latest_version_str = latest_tag_name.lstrip('v')
            release_notes = latest_release.get("body", "No release notes available.")
            
            print(f"{GREEN}New version available! Current: {self.current_version}, Latest: {latest_version_str}{RESET}")
            print(f"{BLUE}\nRelease Notes:{RESET}")
            print(f"{BLUE}{release_notes}{RESET}")
            print(f"{BLUE}" + "-" * 20 + f"{RESET}") # Separator for clarity

            # Use input for confirmation instead of messagebox
            user_response = input(
                f"{BLUE}A new version (v{latest_version_str}) is available.\n"
                f"You are currently on version v{self.current_version}.\n"
                f"Do you want to download and install it now? (yes/no): {RESET}"
            ).lower().strip()

            if user_response in ['yes', 'y']:
                temp_exe_path = self.download_new_version(latest_release)
                if temp_exe_path:
                    if self.update_application(temp_exe_path):
                        sys.exit(0) # Exit the current application
            else:
                print(f"{BLUE}Update cancelled by user.{RESET}")
        else:
            print(f"{BLUE}No new updates available. You are running the latest version.{RESET}")

    def _restart_application(self, current_exe_path, temp_exe_path):
        """Restarts the application using WScript.Shell to replace the executable."""
        shell = win32com.client.Dispatch("WScript.Shell")
        
        # Commands to be executed in a new command prompt
        # 0 means hide the window, 1 means show it. 
        # 'True' means wait for the command to complete, 'False' means don't wait.
        commands = [
            f'timeout /t 2 /nobreak > NUL',
            f'del "{current_exe_path}"',
            f'rename "{temp_exe_path}" "{os.path.basename(current_exe_path)}"',
            f'start "" "{current_exe_path}"'
        ]
        
        # The command is wrapped in `cmd /c` to ensure it runs in a command shell
        full_command = 'cmd /c "' + ' & '.join(commands) + '"'
        
        try:
            shell.Run(full_command, 0, False) # Run hidden and don't wait
        except Exception as e:
            print(f"{RED}Failed to restart application using WScript.Shell: {e}{RESET}")
            # Fallback to batch script if WScript.Shell fails
            self._restart_with_batch_fallback(current_exe_path, temp_exe_path)

    def _restart_with_batch_fallback(self, current_exe_path, temp_exe_path):
        """Fallback to batch script if WScript.Shell fails, with logging."""
        script_path = os.path.join(os.path.dirname(current_exe_path), "restart_app.bat")
        log_file = os.path.join(os.path.dirname(current_exe_path), "log_bat.txt")
        with open(script_path, "w") as f:
            f.write("@echo off\n")
            f.write(f'echo %date% %time% - Starting update >> "{log_file}"\n')
            f.write("timeout /t 2 /nobreak > NUL\n")
            f.write(f'echo %date% %time% - Deleting old executable >> "{log_file}"\n')
            f.write(f"del \"{current_exe_path}\"\n")
            f.write(f'echo %date% %time% - Renaming new executable >> "{log_file}"\n')
            f.write(f"rename \"{temp_exe_path}\" \"{os.path.basename(current_exe_path)}\"\n")
            f.write(f'echo %date% %time% - Restarting application >> "{log_file}"\n')
            f.write(f'start "" "{current_exe_path}"\n')
            f.write(f'echo %date% %time% - Update script finished >> "{log_file}"\n')
            f.write("(goto) 2>nul & del \"%~f0\"\n")
        subprocess.Popen([script_path], shell=True, creationflags=subprocess.DETACHED_PROCESS)

# Example Usage (for testing purposes, not for direct execution in main app)
if __name__ == "__main__":
    # Replace with your actual repo owner, repo name, and current version
    # For testing, you might use a dummy repo or your own test repo
    # current_app_version should ideally come from a version file or build process
    updater = AppUpdater(
        repo_owner="C1ean-dev", 
        repo_name="FileStorageIndexer",
        current_version="1" # TODO: Dynamically get current version (e.g., from build.yml run number)
    )
    updater.check_for_updates()
