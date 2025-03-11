import os
import json
import requests
import threading

class ParticleLinuxSDK:
    CONFIG_PATH = os.path.expanduser("~/.particle/particle.config.json")
    DISTRO_VERSIONS_PATH = "/etc/particle/distro_versions.json"

    def __init__(self):
        self.config = self._load_config()
        self.distro_versions = self._load_distro_versions()
        self.access_token = self.config.get("access_token")
        self.username = self.config.get("username")
        self.device_id = self.config.get("deviceID")
        self.base_url = self.config.get("api_base_url", "https://api.particle.io/v1")
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def _load_config(self):
        """Load the Particle config file."""
        try:
            with open(self.CONFIG_PATH, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            raise Exception("Failed to load config file.")

    def _load_distro_versions(self):
        """Load the distro versions file."""
        try:
            with open(self.DISTRO_VERSIONS_PATH, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def get_user_details(self):
        """Retrieve the user's email from the config file."""
        return self.username

    def get_device_info(self):
        """Fetch details of the device listed in the config file."""
        if not self.device_id:
            raise Exception("Device ID not found in config file.")
        url = f"{self.base_url}/devices/{self.device_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_version_details(self):
        """Get firmware and hardware versions from API and system distro info."""
        device_info = self.get_device_info()
        return {
            "firmware_version": device_info.get("firmware_version", "Unknown"),
            "product_id": device_info.get("product_id", "Unknown"),
            "platform_id": device_info.get("platform_id", "Unknown"),
            "distro_stack": self.distro_versions.get("distro", {}).get("stack", "Unknown"),
            "distro_version": self.distro_versions.get("distro", {}).get("version", "Unknown"),
            "distro_variant": self.distro_versions.get("distro", {}).get("variant", "Unknown"),
            "ubuntu_source": self.distro_versions.get("src", {}).get("ubuntu_20_04", "Unknown"),
            "quectel_firmware": self.distro_versions.get("src", {}).get("quectel_bp_fw", "Unknown"),
            "syscon_firmware": self.distro_versions.get("src", {}).get("syscon_firmware", "Unknown")
        }

    def publish_event(self, event_name, data, private=True, ttl=60):
        """Publish an event to the Particle Cloud."""
        url = f"{self.base_url}/devices/events"
        payload = {
            "name": event_name,
            "data": data,
            "private": "true" if private else "false",
            "ttl": ttl
        }
        response = requests.post(url, headers=self.headers, data=payload)
        return response.json()

    def subscribe_event(self, event_name, callback):
        """Subscribe to a Particle event stream."""
        url = f"{self.base_url}/devices/events/{event_name}"
        response = requests.get(url, headers=self.headers, stream=True)
        
        def event_listener():
            for line in response.iter_lines():
                if line:
                    event_data = json.loads(line)
                    callback(event_data)
        
        thread = threading.Thread(target=event_listener, daemon=True)
        thread.start()
        return thread

# Example usage
if __name__ == "__main__":
    sdk = ParticleLinuxSDK()
    print("User Email:", sdk.get_user_details())
    print("Device Info:", sdk.get_device_info())
    print("Version Details:", sdk.get_version_details())
    
    # Example publishing an event
    print("Publishing event:", sdk.publish_event("test_event", "Hello Particle!"))
    
    # Example subscribing to an event
    def handle_event(event):
        print("Received event:", event)
    
    sdk.subscribe_event("test_event", handle_event)
