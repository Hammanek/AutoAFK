"""Version checker for AutoAFK"""
import requests
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Import version and repo from main module
import __main__
CURRENT_VERSION = __main__.VERSION
GITHUB_API_URL = __main__.GITHUB_API_URL


class VersionChecker:
    """Check for updates on GitHub"""
    
    @staticmethod
    def get_latest_version() -> Optional[str]:
        """
        Get latest version from GitHub releases
        
        Returns:
            Latest version string or None if failed
        """
        try:
            response = requests.get(GITHUB_API_URL, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            latest_version = data.get('tag_name', '').lstrip('v')
            
            return latest_version
        except requests.RequestException as e:
            logger.warning(f"Failed to check for updates: {e}")
            return None
        except Exception as e:
            logger.error(f"Error checking version: {e}")
            return None
    
    @staticmethod
    def compare_versions(current: str, latest: str) -> int:
        """
        Compare two version strings
        
        Args:
            current: Current version (e.g., "2.0.0")
            latest: Latest version (e.g., "2.1.0")
            
        Returns:
            -1 if current < latest (update available)
             0 if current == latest (up to date)
             1 if current > latest (ahead of release)
        """
        try:
            current_parts = [int(x) for x in current.split('.')]
            latest_parts = [int(x) for x in latest.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(current_parts), len(latest_parts))
            current_parts += [0] * (max_len - len(current_parts))
            latest_parts += [0] * (max_len - len(latest_parts))
            
            for c, l in zip(current_parts, latest_parts):
                if c < l:
                    return -1
                elif c > l:
                    return 1
            
            return 0
        except Exception as e:
            logger.error(f"Error comparing versions: {e}")
            return 0
    
    @staticmethod
    def check_for_updates() -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if update is available
        
        Returns:
            Tuple of (update_available, current_version, latest_version)
        """
        latest = VersionChecker.get_latest_version()
        
        if latest is None:
            return False, CURRENT_VERSION, None
        
        comparison = VersionChecker.compare_versions(CURRENT_VERSION, latest)
        
        if comparison < 0:
            logger.info(f"Update available: {CURRENT_VERSION} -> {latest}")
            return True, CURRENT_VERSION, latest
        elif comparison == 0:
            logger.info(f"You are running the latest version: {CURRENT_VERSION}")
            return False, CURRENT_VERSION, latest
        else:
            logger.info(f"You are ahead of the latest release: {CURRENT_VERSION} > {latest}")
            return False, CURRENT_VERSION, latest
    
    @staticmethod
    def get_release_notes(version: str) -> Optional[str]:
        """
        Get release notes for a specific version
        
        Args:
            version: Version to get notes for
            
        Returns:
            Release notes or None if failed
        """
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/v{version}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            return data.get('body', 'No release notes available')
        except Exception as e:
            logger.error(f"Error getting release notes: {e}")
            return None
    
    @staticmethod
    def get_download_url() -> str:
        """Get download URL for latest release"""
        return f"https://github.com/{GITHUB_REPO}/releases/latest"


def check_version_on_startup(show_message: bool = True) -> None:
    """
    Check for updates on startup
    
    Args:
        show_message: Whether to show message even if up to date
    """
    try:
        update_available, current, latest = VersionChecker.check_for_updates()
        
        if update_available:
            logger.warning("=" * 60)
            logger.warning(f"UPDATE AVAILABLE: {current} -> {latest}")
            logger.warning(f"Download: {VersionChecker.get_download_url()}")
            logger.warning("=" * 60)
        elif show_message and latest:
            logger.info(f"✓ Running latest version: {current}")
    except Exception as e:
        logger.debug(f"Version check failed: {e}")


if __name__ == "__main__":
    # Test version checker
    logging.basicConfig(level=logging.INFO)
    
    print(f"Current version: {CURRENT_VERSION}")
    print(f"Checking for updates...")
    
    update_available, current, latest = VersionChecker.check_for_updates()
    
    if latest:
        print(f"Latest version: {latest}")
        if update_available:
            print("Update available!")
            print(f"Download: {VersionChecker.get_download_url()}")
        else:
            print("You are up to date!")
    else:
        print("Could not check for updates")
