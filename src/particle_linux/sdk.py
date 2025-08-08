import os
import json
import requests
import threading

class ParticleLinuxSDK:
    CONFIG_PATH = os.getenv("CONFIG_PATH", "/home/particle/.particle/particle.config.json")
    DISTRO_VERSIONS_PATH = os.getenv("DISTRO_VERSIONS_PATH", "/etc/particle/distro_versions.json")

    def __init__(self):
        self.emulation_mode = not (os.path.exists(self.CONFIG_PATH) and os.path.exists(self.DISTRO_VERSIONS_PATH))

        if self.emulation_mode:
            print("⚠️ Running in EMULATION mode: Config and distro files are missing.")

            #print out all the files in the config and distro paths
            print("Files in config path:")
            for file in os.listdir(os.path.dirname(self.CONFIG_PATH)):
                print(file)
            print("Files in distro path:")
            for file in os.listdir(os.path.dirname(self.DISTRO_VERSIONS_PATH)):
                print(file)

            self.config = self._get_emulated_config()
            self.distro_versions = self._get_emulated_distro_versions()
        else:
            self.config = self._load_config()
            self.distro_versions = self._load_distro_versions()

        self.access_token = self.config.get("access_token", None)
        self.username = self.config.get("username", "Unknown")
        self.device_id = self.config.get("deviceId", None)
        self.product_id = self.config.get("productId", None)
        self.base_url = self.config.get("api_base_url", "https://api.particle.io/v1")
        self.headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}

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

    def _get_emulated_config(self):
        """Return a mock config for emulation mode."""
        return {
            "access_token": "mock_access_token",
            "username": "emulated_user@particle.io",
            "deviceID": "mock_device_id",
            "api_base_url": "https://api.particle.io/v1"
        }

    def _get_emulated_distro_versions(self):
        """Return mock distro versions for emulation mode."""
        return {
            "distro": {
                "stack": "emulated-stack",
                "version": "0.0.1-emulated",
                "variant": "emulated"
            },
            "src": {
                "ubuntu_20_04": "mock-image",
                "quectel_bp_fw": "mock-fw",
                "syscon_firmware": "mock-syscon"
            }
        }


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

    def publish_event(self, event_name, data, ttl=60):
        """Publish an event to the Particle Cloud."""

        #drop emulation mode
        if self.emulation_mode:
            print("dropping package {data} for event {event_name} in emulation mode")
            return

        url = f"{self.base_url}/products/{self.product_id}/events"
        payload = {
            "name": event_name,
            "data": data,
            "as_device_id": self.device_id,
            "private": "true",
            "ttl": ttl
        }
        response = requests.post(url, headers=self.headers, data=payload)
        return response.json()

    def subscribe_event(self, event_name, callback):
        """Subscribe to a Particle event stream."""

        if self.emulation_mode:
            print("dropping package {data} for event {event_name} in emulation mode")
            return

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
