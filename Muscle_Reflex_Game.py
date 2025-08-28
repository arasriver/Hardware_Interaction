import streamlit as st
import time
import numpy as np
from Mindrove import MindroveDevice

THRESHOLD = 50.0
ROUND_DURATION = 2
TOTAL_ROUNDS = 10

device = MindroveDevice()
device.start_stream()

st.title("Muscle Reflex Game")

if st.button("Start Game"):
    score = 0
    for round_number in range(1, TOTAL_ROUNDS + 1):
        st.write(f"Round {round_number}/{TOTAL_ROUNDS}")
        st.write("Contract now!")

        start_time = time.time()
        contracted = False

        while time.time() - start_time < ROUND_DURATION:
            emg_chunk = device.get_data_chunk()
            if emg_chunk.size > 0:
                strength = np.max(emg_chunk)
                if strength > THRESHOLD:
                    score += 1
                    contracted = True
                    st.write(f"Success! EMG: {strength:.2f}")
                    break
            time.sleep(0.1)

        if not contracted:
            st.write("Missed!")

        st.write(f"Current score: {score}")
        st.markdown("---")
        time.sleep(0.5)

    st.write(f"Game Over! Final Score: {score}")

device.stop()
