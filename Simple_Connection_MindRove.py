from Mindrove import MindroveDevice
import time
import numpy as np

threshold = 30
counter = 0
device = MindroveDevice()
device.start_stream()

print("Tight your fist:")
last_contradiction_time = time.time()

try:
    while True:
        emg_chunk = device.get_data_chunk()
        if emg_chunk.size > 0:
            strength = np.mean(emg_chunk)
            print(f"{counter}  |  EMG value: {strength:.2f}")
            if strength > threshold:
                counter += 1
                print(counter)
                last_contradiction_time = time.time()

        if time.time() - last_contradiction_time > 5:
            print("Time to exit!")
            break

        time.sleep(1)

finally:
    device.stop()