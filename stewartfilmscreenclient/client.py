"""Stewart Filmscreen Client."""

import asyncio
import logging
import telnetlib3

from .protocol import StewartFilmscreenProtocol

log = logging.getLogger(__name__)

PROMPT_USERNAME = "User:"
PROMPT_PASSWORD = "Password:"
PROMPT_CONNECTED = "Connected:"


class StewartFilmscreenClient:
    """Main class for Stewart Filmscreen Client."""
    def __init__(self, host, port, username, password, reconnect_timeout=60):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._reconnect_timeout = reconnect_timeout

        self._reader = None
        self._writer = None
        self._command_queue = []

        self._running = False
        self._connected = False

        self._disconnect_event = asyncio.Event()
        self._send_command_event = asyncio.Event()

        self._connection_monitor_task = None
        self._listen_task = None
        self._command_queue_task = None

        self._state_message_callbacks = []

    async def async_connect(self):
        """Connects client."""
        if await self._async_establish_connection():
            self._running = True
            self._connected = True
        else:
            return False

        await self._async_start_services()

        return True

    def is_connected(self):
        """Provides CVM connection status."""
        return self._connected

    def register_state_message_callback(self, callback):
        """Register a callback to be called when a command is echoed back."""
        if callback not in self._state_message_callbacks:
            self._state_message_callbacks.append(callback)

    def deregister_state_message_callback(self, callback):
        """Deregister a callback to stop receiving state message updates."""
        if callback in self._state_message_callbacks:
            self._state_message_callbacks.remove(callback)

    async def _async_notify_state_message_callbacks(self, command_data):
        """Notify all registered callbacks with the parsed command data."""
        for callback in self._state_message_callbacks:
            await callback(command_data)

    async def _async_connection_monitor(self):
        """Maintains proper connection to CVM."""
        while self._running:
            if not self._connected:
                try:
                    await self._async_establish_connection()
                    self._connected = True
                    self._disconnect_event.clear()

                    await self._async_start_services()

                except Exception as error:
                    log.debug(
                        "Connection failed: %s, reconnecting in %s seconds",
                        error,
                        self._reconnect_timeout,
                    )
            else:
                await self._disconnect_event.wait()

            await asyncio.sleep(self._reconnect_timeout)

    async def _async_establish_connection(self):
        """Establishes connection to CVM."""
        self._reader, self._writer = await telnetlib3.open_connection(
            self._host, self._port
        )
        return await self._async_authenticate()

    async def _async_authenticate(self):
        """Authenticates to CVM."""
        while not self._connected:
            try:
                data = await self._reader.readuntil(b":")
                data_str = data.decode("utf-8")

                if data_str == PROMPT_USERNAME:
                    log.debug("Received user prompt.")
                    self._writer.write(self._username + "\r\n")
                    await self._writer.drain()

                if data_str == PROMPT_PASSWORD:
                    log.debug("Received prompt prompt.")
                    self._writer.write(self._password + "\r\n")
                    await self._writer.drain()

                if data_str == PROMPT_CONNECTED:
                    log.debug("Received connected prompt.")
                    await self._reader.readuntil(b"\r\n")
                    return True

            except Exception as error:
                log.debug("Disconnected while authenticating: %s", error)
                return False

    async def _async_command_queue(self):
        self._command_queue = []
        self._send_command_event.clear()

        while self._running:
            try:
                while len(self._command_queue) > 0:
                    command = self._command_queue.pop(0)
                    self._writer.write(command + "\r\n")
                    await self._writer.drain()

                    # space out commands to not overwhelm server
                    await asyncio.sleep(1)

                await self._send_command_event.wait()
                self._send_command_event.clear()

            except Exception as error:
                log.debug(
                    "Disconnected: %s, reconnecting in %s seconds",
                    error,
                    {self._reconnect_timeout},
                )
                self._disconnect()

    async def _async_listen(self):
        """Listens for state messages from CVM."""
        while self._running:
            try:
                data = await self._reader.readuntil(b"\r\n")
                data_str = data.decode("utf-8").strip()

                log.debug("Received: %s", data_str)
                parsed_message = StewartFilmscreenProtocol.parse_message(data_str)

                if parsed_message is not None:
                    await self._async_notify_state_message_callbacks(parsed_message)

            except Exception as error:
                log.debug(
                    "Disconnected: %s, reconnecting in %s seconds",
                    error,
                    {self._reconnect_timeout},
                )
                self._disconnect()

    async def _async_start_services(self):
        """Starts services required by client."""
        self._connection_monitor_task = asyncio.get_running_loop().create_task(
            self._async_connection_monitor()
        )
        self._listen_task = asyncio.get_running_loop().create_task(self._async_listen())
        self._command_queue_task = asyncio.get_running_loop().create_task(
            self._async_command_queue()
        )
        await asyncio.sleep(1)

    def _disconnect(self):
        """Disconnect client and perform cleanup."""
        self._connected = False

        for task in (self._listen_task, self._command_queue_task):
            if task is not None:
                task.cancel()

        if self._writer:
            self._writer.close()

        self._disconnect_event.set()

    async def async_send_command(self, command):
        """Sends command."""
        self._command_queue.append(command)
        self._send_command_event.set()

    async def async_recall_preset(self, preset_number):
        """Recalls motor settings from desired preset."""
        command = StewartFilmscreenProtocol.command(
            StewartFilmscreenProtocol.MOTOR_ALL,
            StewartFilmscreenProtocol.COMMAND_RECALL,
            preset_number,
        )
        self._command_queue.append(command)
        self._send_command_event.set()

    async def async_store_preset(self, preset_number):
        """Stores motor settings at desired preset."""
        command = StewartFilmscreenProtocol.command(
            StewartFilmscreenProtocol.MOTOR_ALL,
            StewartFilmscreenProtocol.COMMAND_STORE,
            preset_number,
        )
        self._command_queue.append(command)
        self._send_command_event.set()

    def close(self):
        """Closes and disconnects client."""
        self._running = False
        self._connection_monitor_task.cancel()
        self._disconnect()
