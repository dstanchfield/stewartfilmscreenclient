# StewartFilmscreenClient

StewartFilmscreenClient is an asynchronous Python client for controlling and monitoring a a Stewart Filmscreen CVM. This library enables seamless integration with Stewart Filmscreen CVM, providing capabilities such as sending commands, recalling presets, and registering callbacks for state changes.

## Features

- Asynchronous API.
- Connect and authenticate with CVM.
- Monitors connection to CVM and reconnects automatically.
- Send various commands to control CVM.
- Register and deregister callbacks for CVM state updates.
- Store and recall motor settings presets.

## Installation

StewartFilmscreenClient is currently available directly from the source. To install, use the following command:

```bash
pip install git+https://github.com/dstanchfield/stewartfilmscreenclient.git
```

## Usage

Here is a basic example of how to use the StewartFilmscreenClient:

```python
import asyncio
from stewart_filmscreen_client import StewartFilmscreenClient, StewartFilmscreenProtocol

async def async_handle_events(e):
    print(e)

async def main():
    client = StewartFilmscreenClient('127.0.0.1', 23, 'csidealer', '4212color')
    client.register_state_message_callback(async_handle_events)
    await client.async_connect()
    await client.async_send_command(StewartFilmscreenProtocol.query(
        StewartFilmscreenProtocol.MOTOR_A,
        StewartFilmscreenProtocol.QUERY_POSITION)
    )
    await client.async_send_command(StewartFilmscreenProtocol.command(
        StewartFilmscreenProtocol.MOTOR_A,
        StewartFilmscreenProtocol.COMMAND_UP)
    )
    client.close()

asyncio.run(main())
```

## API Reference

- `async_connect()`: Asynchronously connects to the device.
- `is_connected()`: Checks if the client is currently connected.
- `register_state_message_callback(callback)`: Registers a callback for CVM updates.
- `deregister_state_message_callback(callback)`: Deregisters a CVM update callback.
- `async_send_command(command)`: Sends a command to the CVM.
- `async_recall_preset(preset_number)`: Recalls a preset setting.
- `async_store_preset(preset_number)`: Stores a preset setting.
- `close()`: Closes the connection and performs cleanup.

## Contributions

Contributions to StewartFilmscreenClient are welcome. Please ensure that your code adheres to the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

*Note: This integration is not officially affiliated with or endorsed by Stewart Filmscreen.*