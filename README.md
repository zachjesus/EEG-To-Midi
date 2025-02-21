# EEG to OSC Bridge

This Python script bridges EEG data streams to OSC messages, converting brainwave data (delta, theta, alpha, and beta waves) into MIDI-compatible values. It's designed to work with Lab Streaming Layer (LSL) for EEG input and sends the processed data via OSC messages to your desired ip/port.

## Features

- Reads EEG data from LSL streams
- Processes four brainwave bands: delta, theta, alpha, and beta
- Applies smoothing and normalization to the signals
- Converts normalized values to MIDI range (0-127)
- Sends data as OSC messages

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/zachjesus/EEG-To-Midi.git
cd EEG-To-Midi
```

2. Install the required Python packages:
```bash
pip install numpy
pip install scipy
pip install pylsl
pip install python-osc
```

## Configuration

The script includes several configurable constants at the top:

```python
# Maximum values for brainwaves (µV)
delta_max_uv = 40
theta_max_uv = 40
alpha_max_uv = 40
beta_max_uv  = 40

# Update period (seconds)
moving_average_period_sec = 0.1

# Smoothing level
smooth_level = 2

# Network settings
ip = "127.0.0.1"
port = 8001
```

Adjust these values based on your needs.

## Usage

1. Start your EEG device and ensure it's streaming data via LSL

2. Run the script:
```bash
python eegToMidi.py
```

3. The script will:
   - Look for available LSL streams
   - Connect to the first available EEG stream
   - Process the data
   - Send OSC messages to the specified IP and port
   
You can run the EEG on one computer, and this program on another. By connecting them via ethernet and setting up the networking correctly it should be seamless. 

## OSC Message Format

The script sends OSC bundles containing four messages:
- `/delta_midi` : MIDI value (0-127) for delta waves
- `/theta_midi` : MIDI value (0-127) for theta waves
- `/alpha_midi` : MIDI value (0-127) for alpha waves
- `/beta_midi`  : MIDI value (0-127) for beta waves

## Advice 
  - Mess with the moving average period
  - Setting correct max numbers for the brainwave is essential for smooth function (should be done based on testing)

I did not add a minimum constant, and used zero, however, it may be set where the smoothstep function is called

## Example MAX Usage

![image](https://github.com/user-attachments/assets/ef6cd470-7da8-49d9-9674-f6ec9b759d30)

Example is using CNMAT o.dot for more control over OSC messages. See: https://github.com/CNMAT/CNMAT-odot.
