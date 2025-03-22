# Computer Lab Control System

A networked solution for managing computer labs, classrooms, or testing environments. This system allows instructors to open websites simultaneously on all student computers with a single click.

## Overview

The Computer Lab Control System is designed for educational environments where an instructor needs to control multiple computers remotely. It's particularly useful for:

- Standardizing exam access across all computers
- Opening educational resources for all students simultaneously
- Managing computer lab sessions efficiently
- Streamlining technical setup time for classroom activities

## Features

- **Centralized Control**: Manage all student computers from a single control panel
- **One-Click URL Distribution**: Open websites on all connected computers simultaneously
- **Multiple URL Support**: Send multiple links at once
- **Saved Links Library**: Store frequently used URLs for quick access
- **Real-time Monitoring**: See connected clients and connection status
- **Auto-reconnect**: Clients automatically reconnect if connection is lost
- **Cross-platform**: Works on Windows, macOS, and Linux

## Components

### Server (Teacher/Control Computer)

The server application provides a graphical interface with:

- Server status controls (start/stop)
- Single and multiple URL input fields
- Saved links management
- Connected client counter
- Activity log
- Network settings configuration

### Client (Student Computers)

The client application runs in the background and:

- Connects to the server automatically
- Opens websites as directed by the server
- Reconnects automatically if the connection drops
- Can be configured to start on system boot

## Installation

### Prerequisites

- Python 3.6+ installed on all computers
- All computers must be on the same network
- Network must allow TCP traffic on the configured port (default: 9999)

### Server Setup

1. Clone this repository or download the source code
2. Navigate to the project directory
3. Run the server application:

```bash
python server.py
```

4. The server interface will appear, allowing you to configure and start the server

### Client Setup

1. Copy the `client.py` file to each student computer
2. Run the client with the server's IP address:

```bash
python client.py [SERVER_IP_ADDRESS] [PORT]
```

For example:
```bash
python client.py 192.168.1.10 9999
```

### Auto-start Configuration

#### Windows:

Create a batch file (`.bat`) with the following content:

```batch
@echo off
python C:\path\to\client.py SERVER_IP_ADDRESS 9999
```

Add this batch file to the Windows Startup folder.

#### macOS:

Create a launch agent plist file in `~/Library/LaunchAgents/com.lab-control-client.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.lab-control-client</string>
    <key>ProgramArguments</key>
    <array>
        <string>python3</string>
        <string>/path/to/client.py</string>
        <string>SERVER_IP_ADDRESS</string>
        <string>9999</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load the launch agent:
```bash
launchctl load ~/Library/LaunchAgents/com.lab-control-client.plist
```

#### Linux:

Add a startup entry in `/etc/xdg/autostart/lab-client.desktop`:

```
[Desktop Entry]
Type=Application
Name=Lab Control Client
Exec=python3 /path/to/client.py SERVER_IP_ADDRESS 9999
Terminal=false
```

## Usage

### Starting the Server

1. Launch the server application
2. Navigate to the "Settings" tab to configure host and port
3. Click "Start Server" in the Control Panel tab

### Opening URLs on Client Computers

#### Single URL:
1. Enter the URL in the designated field
2. Click "Open on All Computers"

#### Multiple URLs:
1. Enter each URL on a separate line in the "Open Multiple Links" section
2. Click "Open All Links"

### Managing Saved Links

1. Navigate to the "Saved Links" tab
2. Add new links with descriptive names
3. Select a saved link and click "Open Selected Link" to send it to all computers

## Troubleshooting

### Connection Issues

- Verify all computers are on the same network
- Check firewall settings on server and client computers
- Ensure the correct IP address and port are being used
- Check the server log for connection failures

### Browser Issues

- The system uses the default browser on client computers
- Make sure browsers are updated and working properly
- If specific browser configurations are needed, they must be set up on each client

## Security Considerations

- This system is designed for use in controlled environments on secured networks
- There is no authentication system included
- It's recommended to use this on a private network segment
- Consider firewall rules to restrict access to the server port

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
