import collections
import logging
from typing import Optional, Text
import numpy as np
import pyaudio
import queue
import scipy
import scipy.signal
import wave
import webrtcvad


class UtteranceService:
    """The UtteranceService is responsible for recording complete utterances for the speech transcriber."""

    format = pyaudio.paInt16
    channels: int = 1
    sample_rate: int = 16000
    blocks_per_second: int = 50

    block_size: int = sample_rate // blocks_per_second

    frame_duration_ms: int = property(
        lambda self: 1000 * self.block_size // self.sample_rate)

    buffer_queue: queue.Queue
    device_index: int
    input_rate: int
    block_size_input: int
    pa: pyaudio.PyAudio
    stream: pyaudio.Stream
    vad: webrtcvad.Vad

    def __init__(self, aggressiveness: int = 1, device_index: int = None, input_rate: int = 16000,
                 filename: Optional[str] = None, lowpass_frequency: int = 65, highpass_frequency: int = 4000):
        self.buffer_queue = queue.Queue()
        self.device_index = device_index
        self.input_rate = input_rate
        self.block_size_input = self.input_rate // self.blocks_per_second
        self.pa = pyaudio.PyAudio()
        self.stream = self._create_stream(filename)
        self.vad = webrtcvad.Vad(aggressiveness)

        logging.info("Found input sound devices: " + '; '.join([
            f"({i}) {self.pa.get_device_info_by_host_api_device_index(0, i).get('name')}"
            for i in range(0, self.pa.get_host_api_info_by_index(0)['deviceCount'])
            if self.pa.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0
        ]))

        if device_index:
            logging.info(f"Using input sound device index: {device_index}")
        else:
            logging.info(
                f"Using default input sound device index: {self.pa.get_host_api_info_by_index(0)['defaultInputDevice']}")

        self._init_filter(lowpass_frequency, highpass_frequency)

    def _create_stream(self, filename: Optional[str] = None):
        """Creates a new audio stream.

        Args:
            filename (str): The filename to store complete utterances at.
        """

        def callback(in_data, frame_count, time_info, status):
            if self.chunk is not None:
                in_data = self.wf.readframes(self.chunk)
            self.buffer_queue.put(in_data)
            return (None, pyaudio.paContinue)

        kwargs = {
            'format': self.format,
            'channels': self.channels,
            'rate': self.input_rate,
            'input': True,
            'frames_per_buffer': self.block_size_input,
            'stream_callback': callback
        }

        self.chunk = None
        if self.device_index:  # non-default device_index selected
            kwargs['input_device_index_index'] = self.device_index
        elif filename is not None:
            self.chunk = 320
            self.wf = wave.open(filename, 'rb')

        stream = self.pa.open(**kwargs)
        stream.start_stream()

        return stream

    def _end_stream(self, stream):
        """Terminates a given stream.

        Args:
            stream (Stream): The stream to terminate.
        """

        stream.stop_stream()
        stream.close()

    def _destroy(self):
        """Destroys the stream and terminates recording with PyAudio."""

        self._end_stream(self.stream)
        self.pa.terminate()

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
            pass
        finally:
            self._destroy()
