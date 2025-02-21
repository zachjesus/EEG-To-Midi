import numpy as np
import math 
from pylsl import StreamInlet, resolve_streams
from pythonosc.udp_client import SimpleUDPClient
from pythonosc import osc_bundle_builder, osc_message_builder
from scipy.special import comb

# max for brainwaves, needed for smoothstep
delta_max_uv = 40
theta_max_uv = 40
alpha_max_uv = 40
beta_max_uv  = 40

# period of the moving average in seconds (also the rate midi notes will be sent out at)
moving_average_period_sec = .1

# for the smooth step func
smooth_level = 2

# networking constants for the clien (where should it send to)  
ip = "127.0.0.1"
port = 8001

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

def main():
    # first resolve an EEG stream on the lab network
    print("looking for an EEG stream...")
    streams = resolve_streams()

    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])
    client = SimpleUDPClient(ip, port)

    while True:
        # lists for moving averages
        delta_sample_list = []
        theta_sample_list = []
        alpha_sample_list = []
        beta_sample_list  = []

        # grabbing first sample and its start time
        startTime = inlet.pull_sample()[1]
        currTime = startTime

	# calculate moving average based on chosen time between samples
        while currTime <= startTime + moving_average_period_sec:
            sample, timeStamp = inlet.pull_sample()
            currTime = timeStamp

            # split data into 4 waves
            delta_uv = sample[0]
            theta_uv = sample[1]
            alpha_uv = sample[2]
            beta_uv  = sample[3]

            # add data to respective lists
            delta_sample_list.append(delta_uv)
            theta_sample_list.append(theta_uv)
            alpha_sample_list.append(alpha_uv)
            beta_sample_list.append(beta_uv)
        
        # take avg from time_between_sample (seconds)
        delta_uv_avg = mean(delta_sample_list)
        theta_uv_avg = mean(theta_sample_list)
        alpha_uv_avg = mean(alpha_sample_list)
        beta_uv_avg  = mean(beta_sample_list)

        # smooth step 
        delta_smooth = smoothstep(delta_uv_avg, 0, delta_max_uv)
        theta_smooth = smoothstep(theta_uv_avg, 0, theta_max_uv)
        alpha_smooth = smoothstep(alpha_uv_avg, 0, alpha_max_uv)
        beta_smooth  = smoothstep(beta_uv_avg,  0, beta_max_uv)

        # convert to midi
        delta_midi = to_midi(delta_smooth)
        theta_midi = to_midi(theta_smooth)
        alpha_midi = to_midi(alpha_smooth)
        beta_midi  = to_midi(beta_smooth)

        #create osc bundle
        bundle = osc_bundle_builder.OscBundleBuilder(osc_bundle_builder.IMMEDIATELY)
	
	# here is where message structure is defined
        delta_msg = osc_message_builder.OscMessageBuilder(address="/delta_midi")
        delta_msg.add_arg(delta_midi)

        theta_msg = osc_message_builder.OscMessageBuilder(address="/theta_midi")
        theta_msg.add_arg(theta_midi)

        alpha_msg = osc_message_builder.OscMessageBuilder(address="/alpha_midi")
        alpha_msg.add_arg(alpha_midi)

        beta_msg = osc_message_builder.OscMessageBuilder(address="/beta_midi")
        beta_msg.add_arg(beta_midi)

        # add msgs to bundle
        bundle.add_content(delta_msg.build())
        bundle.add_content(theta_msg.build())
        bundle.add_content(alpha_msg.build())
        bundle.add_content(beta_msg.build())

        bundle = bundle.build()

        # send data to MAX
        # recieve data in MAX by using udpreceive 8001 
        client.send(bundle)

if __name__ == "__main__":
    main()