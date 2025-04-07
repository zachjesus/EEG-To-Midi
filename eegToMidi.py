import numpy as np
from pylsl import StreamInlet, resolve_streams
from pythonosc.udp_client import SimpleUDPClient
from pythonosc import osc_bundle_builder, osc_message_builder
from scipy.special import comb
import matplotlib.pyplot as plt
from collections import deque
import time

# max for brainwaves, needed for smoothstep
delta_max_uv = 40
theta_max_uv = 7
alpha_max_uv = 7
beta_max_uv  = 7

# period of the moving average in seconds (also the rate midi notes will be sent out at)
moving_average_period_sec = .1

# for the smooth step func
smooth_level = 3

# networking constants for the clien (where should it send to)  
ip = "127.0.0.1"
port = 8001

history_length = 100
time_points = deque(maxlen=history_length)
delta_midi_history_freq = deque(maxlen=history_length)
theta_midi_history_freq = deque(maxlen=history_length)
alpha_midi_history_freq = deque(maxlen=history_length)
beta_midi_history_freq = deque(maxlen=history_length)
delta_avg_history_freq = deque(maxlen=history_length)
theta_avg_history_freq = deque(maxlen=history_length)
alpha_avg_history_freq = deque(maxlen=history_length)
beta_avg_history_freq = deque(maxlen=history_length)

delta_midi_history_amp = deque(maxlen=history_length)
theta_midi_history_amp = deque(maxlen=history_length)
alpha_midi_history_amp = deque(maxlen=history_length)
beta_midi_history_amp = deque(maxlen=history_length)
delta_avg_history_amp = deque(maxlen=history_length)
theta_avg_history_amp = deque(maxlen=history_length)
alpha_avg_history_amp = deque(maxlen=history_length)
beta_avg_history_amp = deque(maxlen=history_length)

def mean(nums):
    return float(sum(nums)) / max(len(nums), 1)

def smoothstep(x, x_min=0, x_max=1, N=smooth_level):
    x = np.clip((x - x_min) / (x_max - x_min), 0, 1)

    result = 0
    for n in range(0, N + 1):
         result += comb(N + n, n) * comb(2 * N + 1, N - n) * (-x) ** n

    result *= x ** (N + 1)

    return result

def to_midi(smooth_val):
    return round(smooth_val * 127)

def setup_plots():
    plt.ion()  # Turn on interactive mode for real-time plotting
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # MIDI values plot
    ax1.set_title('MIDI Values Over Time Freq')
    ax1.set_ylabel('MIDI Value Freq (0-127)')
    ax1.set_ylim(0, 127)
    
    # Moving averages plot
    ax2.set_title('MIDI Values Over Time Amp')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('MIDI Value Amp (0-127)')
    ax2.set_ylim(0, 127)
    
    # Create line objects
    delta_midi_line_freq, = ax1.plot([], [], 'r-', label='Delta Midi Freq')
    theta_midi_line_freq, = ax1.plot([], [], 'g-', label='Theta Midi Freq')
    alpha_midi_line_freq, = ax1.plot([], [], 'b-', label='Alpha Midi Freq')
    beta_midi_line_freq, = ax1.plot([], [], 'y-', label='Beta Midi Freq')
    
    delta_midi_line_amp, = ax2.plot([], [], 'r-', label='Delta Midi Amp')
    theta_midi_line_amp, = ax2.plot([], [], 'g-', label='Theta Midi Amp')
    alpha_midi_line_amp, = ax2.plot([], [], 'b-', label='Alpha Midi Amp')
    beta_midi_line_amp, = ax2.plot([], [], 'y-', label='Beta Midi Amp')
    
    ax1.legend(loc='upper right')
    ax2.legend(loc='upper right')
    
    plt.tight_layout()
    
    return fig, (delta_midi_line_freq, theta_midi_line_freq, alpha_midi_line_freq, beta_midi_line_freq), \
           (delta_midi_line_amp, theta_midi_line_amp, alpha_midi_line_amp, beta_midi_line_amp)

def update_plots(midi_lines, avg_lines):
    times = list(time_points)
    
    if len(times) > 1:
        # Update MIDI lines
        midi_lines[0].set_data(times, list(delta_midi_history_freq))
        midi_lines[1].set_data(times, list(theta_midi_history_freq))
        midi_lines[2].set_data(times, list(alpha_midi_history_freq))
        midi_lines[3].set_data(times, list(beta_midi_history_freq))
        
        # Update average lines
        avg_lines[0].set_data(times, list(delta_midi_history_amp))
        avg_lines[1].set_data(times, list(theta_midi_history_amp))
        avg_lines[2].set_data(times, list(alpha_midi_history_amp))
        avg_lines[3].set_data(times, list(beta_midi_history_amp))
        
        # Update x-axis limits
        midi_lines[0].axes.set_xlim(min(times), max(times))
        avg_lines[0].axes.set_xlim(min(times), max(times))
        
        plt.draw()
        plt.pause(0.001)

def main():
    # first resolve an EEG stream on the lab network
    print("looking for an EEG stream...")
    streams = resolve_streams()

    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])
    client = SimpleUDPClient(ip, port)
    
    # Setup plotting
    fig, midi_lines, avg_lines = setup_plots()
    start_time = time.time()

    try:
        while True:
            # grabbing first sample and its start time
            sample = inlet.pull_sample()[0]
            print(sample)

            # grab mean freq from lsl
            delta_mean_freq = sample[0]
            theta_mean_freq = sample[1]
            alpha_mean_freq = sample[2]
            beta_mean_freq  = sample[3]

            # grab mean amp
            delta_mean_amp = sample[4]
            theta_mean_amp = sample[5]
            alpha_mean_amp = sample[6]
            beta_mean_amp  = sample[7]

            # smooth step 
            delta_smooth_freq = smoothstep(delta_mean_freq, 1, 4)
            theta_smooth_freq = smoothstep(theta_mean_freq, 4, 8)
            alpha_smooth_freq = smoothstep(alpha_mean_freq, 8, 12)
            beta_smooth_freq  = smoothstep(beta_mean_freq,  12, 30)

            delta_smooth_amp = smoothstep(delta_mean_amp, 0, delta_max_uv)
            theta_smooth_amp = smoothstep(theta_mean_amp, 0, theta_max_uv)
            alpha_smooth_amp = smoothstep(alpha_mean_amp, 0, alpha_max_uv)
            beta_smooth_amp  = smoothstep(beta_mean_amp,  0, beta_max_uv)

            # convert to midi
            delta_midi_freq = to_midi(delta_smooth_freq)
            theta_midi_freq = to_midi(theta_smooth_freq)
            alpha_midi_freq = to_midi(alpha_smooth_freq)
            beta_midi_freq  = to_midi(beta_smooth_freq)

            delta_midi_amp = to_midi(delta_smooth_amp)
            theta_midi_amp = to_midi(theta_smooth_amp)
            alpha_midi_amp = to_midi(alpha_smooth_amp)
            beta_midi_amp  = to_midi(beta_smooth_amp)

            
            # Update plot data
            current_time = time.time() - start_time
            time_points.append(current_time)
            
            # Store MIDI values to graph
            delta_midi_history_freq.append(delta_midi_freq)
            theta_midi_history_freq.append(theta_midi_freq)
            alpha_midi_history_freq.append(alpha_midi_freq)
            beta_midi_history_freq.append(beta_midi_freq)

            delta_midi_history_amp.append(delta_midi_amp)
            theta_midi_history_amp.append(theta_midi_amp)
            alpha_midi_history_amp.append(alpha_midi_amp)
            beta_midi_history_amp.append(beta_midi_amp)
            
            # Update plots
            update_plots(midi_lines, avg_lines)

            #create osc bundle
            bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
        
            # here is where message structure is defined
            delta_msg_freq = osc_message_builder.OscMessageBuilder(address="/delta_midi_freq")
            delta_msg_freq.add_arg(delta_midi_freq)

            theta_msg_freq = osc_message_builder.OscMessageBuilder(address="/theta_midi_freq")
            theta_msg_freq.add_arg(theta_midi_freq)

            alpha_msg_freq = osc_message_builder.OscMessageBuilder(address="/alpha_midi_freq")
            alpha_msg_freq.add_arg(alpha_midi_freq)

            beta_msg_freq = osc_message_builder.OscMessageBuilder(address="/beta_midi_freq")
            beta_msg_freq.add_arg(beta_midi_freq)

            delta_msg_amp = osc_message_builder.OscMessageBuilder(address="/delta_midi_amp")
            delta_msg_amp.add_arg(delta_midi_amp)

            theta_msg_amp = osc_message_builder.OscMessageBuilder(address="/theta_midi_amp")
            theta_msg_amp.add_arg(theta_midi_amp)

            alpha_msg_amp = osc_message_builder.OscMessageBuilder(address="/alpha_midi_amp")
            alpha_msg_amp.add_arg(alpha_midi_amp)

            beta_msg_amp = osc_message_builder.OscMessageBuilder(address="/beta_midi_amp")
            beta_msg_amp.add_arg(beta_midi_amp)

            # add msgs to bundle
            bundle.add_content(delta_msg_freq.build())
            bundle.add_content(theta_msg_freq.build())
            bundle.add_content(alpha_msg_freq.build())
            bundle.add_content(beta_msg_freq.build())

            bundle.add_content(delta_msg_amp.build())
            bundle.add_content(theta_msg_amp.build())
            bundle.add_content(alpha_msg_amp.build())
            bundle.add_content(beta_msg_amp.build())

            bundle = bundle.build()

            # send data to MAX
            # recieve data in MAX by using udpreceive 8001 
            client.send(bundle) 

    except KeyboardInterrupt:
        print("Exiting...")
        plt.close()
    except Exception as e:
        print(e)
        print("restaring...")
        plt.close()
        main()    

if __name__ == "__main__":
    main()
