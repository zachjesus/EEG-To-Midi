# EEG to MIDI

This Python script bridges EEG data streams to OSC messages, converting brainwave amplitude and frequency (delta, theta, alpha, and beta waves) into MIDI-compatible values. It's designed to work with Lab Streaming Layer (LSL) for EEG input and sends the processed data via OSC messages to your desired ip/port. 

## Features

- Reads EEG data (amp and freq) from LSL streams
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
pip install matplotlib
```

## Configuration

The script includes several configurable constants at the top:

```python
# Maximum values for brainwave amplitude (µV)
delta_max_uv = 40
theta_max_uv = 40
alpha_max_uv = 40
beta_max_uv  = 40

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
These are what you pull out and use in MAX to make your silly music.

The script sends OSC bundles containing EIGHT messages:
- `/delta_midi_freq` : Frequency MIDI value (0-127) for delta waves
- `/theta_midi_freq` : Frequency MIDI value (0-127) for theta waves
- `/alpha_midi_freq` : Frequency MIDI value (0-127) for alpha waves
- `/beta_midi_freq`  : Frequency MIDI value (0-127) for beta waves

- `/delta_midi_amp` : Amplitude MIDI value (0-127) for delta waves
- `/theta_midi_amp` : Amplitude MIDI value (0-127) for theta waves
- `/alpha_midi_amp` : Amplitude MIDI value (0-127) for alpha waves
- `/beta_midi_amp`  : Amplitude MIDI value (0-127) for beta waves

## Advice 
  - Setting correct max numbers for the amplitude is essential for proper function (should be done based on testing). I did 
    not add a minimum constant, and used zero, however, it may be set where the smoothstep function is called.
  - You dont have to use my setup, but its a good starting point. This code is based on Barlow parameter extraction. Use        other params. Use other extraction methods. Change the message names, change the bundle formatting. Its all easy to 
    modify, so do so!

## Example MAX Usage

![image](https://github.com/user-attachments/assets/d617b230-7a04-4c56-a59e-6e6469b69842)

Example is using CNMAT o.dot for more control over OSC messages. See: https://github.com/CNMAT/CNMAT-odot.
