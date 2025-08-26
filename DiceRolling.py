import time
import random
import numpy as np
from Mindrove import MindroveDevice


def detect_contraction(emg_chunk, threshold=50.0):
    if emg_chunk.size == 0:
        return False
    strength = np.max(emg_chunk)
    return strength > threshold


if __name__ == "__main__":
    mindrove_device = MindroveDevice()
    mindrove_device.start_stream()
    counter = 0

    try:
        times = int(input("How many dice do you want to roll? "))
        dice = "y"

        while dice != "n":
            if dice == "y":
                for i in range(times):
                    result = (random.randint(1, 6), random.randint(1, 6))
                    counter += 1
                    print(result)
            else:
                print("Invalid choice!")

            print("Contract to roll again, or relax for 5 seconds to stop.")
            time.sleep(5.0)

            emg_chunk = mindrove_device.get_data_chunk()
            if detect_contraction(emg_chunk, threshold=50.0):
                dice = "y"
            else:
                dice = "n"

        print("Thanks for playing!!")
        print(f"Number of Dice Rolling: {counter}")

    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    finally:
        mindrove_device.stop()
