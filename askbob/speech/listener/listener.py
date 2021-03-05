import collections
import logging
import numpy as np
import queue
import scipy
import scipy.signal
import wave
import webrtcvad


class UtteranceService:
    """The UtteranceService is responsible for compiling complete utterances for the speech transcriber."""

    channels: int = 1
    sample_rate: int = 16000
    input_rate: int
    blocks_per_second: int = 50
    reset_buffer_queue: bool = True

    # the number of samples/frames in each block (#samples == #blocks as channels == 1)
    block_size: int = sample_rate // blocks_per_second
    frame_duration_ms: int = property(
        lambda self: 1000 * self.block_size // self.sample_rate)

    buffer_queue: queue.Queue
    vad: webrtcvad.Vad

    def __init__(self, aggressiveness: int = 1, lowpass_frequency: int = 65, highpass_frequency: int = 4000) -> None:
        self.buffer_queue = queue.Queue()
        self.vad = webrtcvad.Vad(aggressiveness)

        self._init_filter(lowpass_frequency, highpass_frequency)

    def _resample(self, data):
        """Resamples audio frames to the sample rate needed for DeepSpeech and webrtcvad (16000Hz).

        The user's microphone may not support the native processing sampling rate of 16000Hz, so audio data will have to be resampled from a sample rate supported by their recording device (input_rate) to sample_rate.
        """
        data16 = np.frombuffer(data, dtype=np.int16)
        resample_size = int(len(data16) * self.sample_rate / self.input_rate)
        resample = scipy.signal.resample(data16, resample_size)
        resample16 = np.array(resample, dtype=np.int16)
        return resample16.tobytes()

    def write_wav(self, filename: str, data):
        """Writes audio frames to a .wav file.

        Args:
            filename (str): The filename of the .wav file to be written.
            data: The audio frames.
        """

        logging.info("Writing wav file: %s", filename)
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(2)  # wf.setsampwidth(self.pa.get_sample_size(format))
        wf.setframerate(self.sample_rate)
        wf.writeframes(data)
        wf.close()

    def _init_filter(self, lowpass_frequency: int, highpass_frequency: int):
        """Initialises the bandpass filter.

        Args:
            lowpass_frequency (int): The lowpass filter cutoff frequency.
            highpass_frequency (int): The highpass filter cutoff frequency.
        """

        nyquist_frequency = 0.5 * self.sample_rate
        self.b, self.a = scipy.signal.filter_design.butter(4, [
            lowpass_frequency / nyquist_frequency,
            highpass_frequency / nyquist_frequency
        ], btype='bandpass')
        self.zi = scipy.signal.signaltools.lfilter_zi(self.b, self.a)

    def _filter(self, data):
        """Applies a bandpass filter to the audio signal."""

        data16 = np.frombuffer(data, dtype=np.int16)

        filtered, self.zi = scipy.signal.signaltools.lfilter(
            self.b, self.a, data16, axis=0, zi=self.zi)

        return np.array(filtered, dtype=np.int16).tobytes()

    def _frames(self):
        """Yields all audio frames from the microphone, blocking if necessary."""
        if self.input_rate == self.sample_rate:
            while True:
                yield self._filter(self.buffer_queue.get())
        else:
            while True:
                yield self._filter(self._resample(self.buffer_queue.get()))

    def utterances(self, padding_ms=300, ratio=0.75):
        """This is a generator that yields series of consecutive audio frames for each utterence, separated by a single None.

        It determines the level of voice activity using the ratio of frames in padding_ms. It uses a buffer to include padding_ms prior to being triggered.

            Example: (frame, ..., frame, None, frame, ..., frame, None, ...)
                      |   utterence   |        |   utterence   |
        """

        triggered = False
        ring_buffer = collections.deque(
            maxlen=(padding_ms // self.frame_duration_ms))

        try:
            for frame in self._frames():
                if len(frame) < 640:
                    return

                is_speech = self.vad.is_speech(frame, self.sample_rate)

                if triggered:
                    yield frame
                    ring_buffer.append((frame, is_speech))
                    num_unvoiced = len(
                        [f for f, speech in ring_buffer if not speech])

                    if num_unvoiced > ratio * ring_buffer.maxlen:
                        triggered = False
                        yield None
                        ring_buffer.clear()
                        if self.reset_buffer_queue:
                            self.buffer_queue = queue.Queue()
                else:
                    ring_buffer.append((frame, is_speech))
                    num_voiced = len(
                        [f for f, speech in ring_buffer if speech])

                    if num_voiced > ratio * ring_buffer.maxlen:
                        triggered = True
                        for f, _ in ring_buffer:
                            yield f
                        ring_buffer.clear()

        except KeyboardInterrupt:
            return
        finally:
            self._destroy()

    def _destroy(self) -> None:
        pass
