# Particle Linux SDK

## Overview
The **Particle Linux SDK** is a Python library that enables communication with **Particle IoT devices** from a Linux host. It allows authentication, device information retrieval, event publishing, and event subscription via the Particle Cloud API.

## Features
- ✅ **Authentication**: Check if the user is logged in.
- ✅ **User Info**: Retrieve the authenticated user's email.
- ✅ **Device Info**: Fetch details of a specific device.
- ✅ **Version Info**: Get firmware and hardware versions.
- ✅ **Event Publishing**: Send events to the Particle Cloud.
- ✅ **Event Subscription**: Listen for Particle events.
- ✅ **Config-based Setup**: Reads credentials and device info from `particle.config.json`.

## Installation

### Prerequisites
- Python 3.7+
- `pip` installed
- A Particle account with an access token

### Install from PyPI (Coming Soon)
```sh
pip install particle-linux-sdk
```

### Install from GitHub
```sh
pip install git+https://github.com/yourusername/particle-linux-sdk.git
```

## Configuration
The SDK reads authentication and device information from `~/.particle/particle.config.json`. Example file:
```json
{
  "access_token": "your-access-token",
  "username": "your-email@particle.io",
  "deviceID": "your-device-id",
  "api_base_url": "https://api.particle.io/v1"
}
```

Additionally, the SDK reads system software information from `/etc/particle/distro_versions.json`.

## Usage

### Initialize SDK
```python
from particle_linux import ParticleLinuxSDK

sdk = ParticleLinuxSDK()
```

### Check Authentication
```python
print("Logged in:", sdk.is_logged_in())
```

### Get User Details
```python
print("User Email:", sdk.get_user_details())
```

### Get Device Info
```python
print("Device Info:", sdk.get_device_info())
```

### Get Version Details
```python
print("Version Details:", sdk.get_version_details())
```

### Publish an Event
```python
print("Publishing event:", sdk.publish_event("test_event", "Hello Particle!"))
```

### Subscribe to an Event
```python
def handle_event(event):
    print("Received event:", event)

sdk.subscribe_event("test_event", handle_event)
```

## Contributing
Contributions are welcome! Feel free to submit issues and pull requests.

## License
This project is licensed under the **Apache 2.0 License**.

```text
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
