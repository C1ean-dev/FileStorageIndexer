
import requests
import os
import sys
import subprocess


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
            print(f"Error fetching latest release info: {e}")
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
            print(f"Executable '{self.executable_name}' not found in the latest release assets.")
            return False

        try:
            print(f"Downloading new version from: {download_url}")
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            # Save the downloaded file to a temporary location
            temp_exe_path = os.path.join(os.path.dirname(sys.executable), f"new_{self.executable_name}")
            with open(temp_exe_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded new version to: {temp_exe_path}")
            return temp_exe_path
        except requests.exceptions.RequestException as e:
            print(f"Error downloading new version: {e}")
            return None

    def update_application(self, temp_exe_path):
        """Replaces the current executable with the new one."""
        current_exe_path = sys.executable
        
        # On Windows, you can't replace a running executable directly.
        # A common workaround is to use a small batch script or a separate process
        # to replace the file after the current application exits.
        
        # For simplicity, this example will attempt a direct replacement,
        # which will likely fail on Windows if the app is running.
        # A more robust solution would involve a separate updater script.

        try:
            # Rename current executable to a backup
            backup_exe_path = current_exe_path + ".old"
            if os.path.exists(backup_exe_path):
                os.remove(backup_exe_path)
            os.rename(current_exe_path, backup_exe_path)
            
            # Move new executable to current executable path
            os.rename(temp_exe_path, current_exe_path)
            print("Application updated successfully. Please restart the application.")
            return True
        except OSError as e:
            print(f"Error updating application: {e}")
            print(f"Failed to update application: {e}\nPlease restart the application manually.")
            # Attempt to revert if rename failed
            if os.path.exists(backup_exe_path) and not os.path.exists(current_exe_path):
                os.rename(backup_exe_path, current_exe_path)
            return False

    def check_for_updates(self):
        """Checks for updates and performs the update if a new version is available."""
        current_exe_path = sys.executable # Define current_exe_path here
        print("Checking for updates...")
        latest_release = self.get_latest_release_info()
        if latest_release and self.is_new_version_available(latest_release):
            latest_tag_name = latest_release.get("tag_name", "N/A")
            latest_version_str = latest_tag_name.lstrip('v')
            print(f"New version available! Current: {self.current_version}, Latest: {latest_version_str}")
            
            # Use input for confirmation instead of messagebox
            user_response = input(
                f"A new version (v{latest_version_str}) is available.\n"
                f"You are currently on version v{self.current_version}.\n"
                "Do you want to download and install it now? (yes/no): "
            ).lower().strip()

            if user_response == 'yes':
                temp_exe_path = self.download_new_version(latest_release)
                if temp_exe_path:
                    if self.update_application(temp_exe_path):
                        # If update was successful, restart the application
                        self._restart_application(current_exe_path)
                        sys.exit(0) # Exit the current application
            else:
                print("Update cancelled by user.")
        else:
            print("No new updates available. You are running the latest version.")

    def _restart_application(self, current_exe_path):
        """Restarts the application using a temporary batch script."""
        # Create a temporary batch file
        script_path = os.path.join(os.path.dirname(current_exe_path), "restart_app.bat")
        
        with open(script_path, "w") as f:
            f.write("@echo off\n")
            f.write(f"timeout /t 1 /nobreak > NUL\n") # Wait for the current process to exit
            f.write(f'start "" "{current_exe_path}"\n') # Start the new executable
            f.write(f"del \"{script_path}\"\n") # Delete the batch script itself
        
        # Execute the batch file and exit the current application
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
