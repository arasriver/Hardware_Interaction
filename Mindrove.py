import time
import numpy as np
from mindrove.board_shim import BoardShim, MindRoveInputParams, BoardIds
from mindrove.exit_codes import MindRoveError
from scipy.signal import butter, filtfilt, iirnotch


def _bandpass(data, fs, low=20.0, high=180.0, order=4):
    nyq = fs * 0.5
    high = min(high, nyq * 0.95)
    low = max(1.0, min(low, high * 0.5))
    b, a = butter(order, [low / nyq, high / nyq], btype='band')
    if data.shape[-1] <= max(len(a), len(b)) * 3:
        return data
    return filtfilt(b, a, data, axis=-1)


def _notch_series(data, fs, freqs=(50.0, 60.0), q=30.0):
    out = data
    for f0 in freqs:
        if f0 < fs * 0.5 * 0.98:
            b, a = iirnotch(f0, q, fs)
            if data.shape[-1] <= max(len(a), len(b)) * 3:
                continue
            out = filtfilt(b, a, out, axis=-1)
    return out


def _moving_average_abs(x, fs, win_sec=0.1):
    w = max(1, int(win_sec * fs))
    kernel = np.ones(w, dtype=np.float64) / w
    return np.apply_along_axis(lambda m: np.convolve(np.abs(m), kernel, mode='valid'), 1, x)


class MindroveDevice:
    """
    Class to manage connection and
    data streaming from a Mindrove EMG device.
    """

    def __init__(self, board_id=BoardIds.MINDROVE_WIFI_BOARD):
        print("Initializing Mindrove Device...")
        try:
            BoardShim.release_all_sessions()
            self.params = MindRoveInputParams()
            self.params.ip_address = "192.168.4.1"
            self.params.ip_port = 4210
            self.board_id = board_id
            self.board = BoardShim(self.board_id, self.params)
            # Prepare session
            self.board.prepare_session()
            # Get key info
            self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
            self.emg_channels = BoardShim.get_emg_channels(self.board_id)

            print(f"Device ready. Board ID: {self.board_id}, Sampling rate: {self.sampling_rate} Hz")

        except MindRoveError as e:
            print(f"Error initializing Mindrove device: {e}")
            self.board = None

    def start_stream(self):
        if self.board and self.board.is_prepared():
            self.board.start_stream()
            print("Stream started...")
        else:
            print("Cannot start stream. Device not ready!")

    def get_data_chunk(self):
        if not self.board or self.board.get_board_data_count() == 0:
            return np.array([])

        all_data = self.board.get_board_data()
        emg_data = all_data[self.emg_channels].astype(np.float64)

        emg_data -= emg_data.mean(axis=1, keepdims=True)
        emg_data = _bandpass(emg_data, self.sampling_rate)
        emg_data = _notch_series(emg_data, self.sampling_rate)
        emg_data = _moving_average_abs(emg_data, self.sampling_rate, win_sec=0.1)

        return emg_data

    def stop(self):
        if self.board and self.board.is_prepared():
            print("Stopping stream and releasing session...")
            self.board.stop_stream()
            self.board.release_session()
            print("Session released.")
        else:
            print("Device is not prepared or already released.")


if __name__ == "__main__":
    mindrove_device = None
    try:
        mindrove_device = MindroveDevice()
        mindrove_device.start_stream()

        for i in range(10):
            emg_chunk = mindrove_device.get_data_chunk()
            if emg_chunk.size > 0:
                print(f"Received EMG data chunk with shape: {emg_chunk.shape}")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    finally:
        if mindrove_device:
            mindrove_device.stop()

