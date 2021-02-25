import pyaudio
import logging

from askbob.speech.listener.listener import UtteranceService


class MicUtteranceService(UtteranceService):

    device_index: int
    pa: pyaudio.PyAudio
    stream: pyaudio.Stream

    def __init__(self, aggressiveness: int = 1, device_index: int = None, input_rate: int = 16000,
                 lowpass_frequency: int = 65, highpass_frequency: int = 4000):
        super().__init__(aggressiveness=aggressiveness,
                         lowpass_frequency=lowpass_frequency,
                         highpass_frequency=highpass_frequency)
        self.device_index = device_index
        self.input_rate = input_rate
        self.pa = pyaudio.PyAudio()
        self.stream = self._create_stream()

        logging.info("Found input sound devices: " + '; '.join([
            f"({i}) {self.pa.get_device_info_by_host_api_device_index(0, i).get('name')}"
            for i in range(0, self.pa.get_host_api_info_by_index(0)['deviceCount'])
            if self.pa.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0
        ]))

        if device_index is not None:
            logging.info(f"Using input sound device index: {device_index}")
        else:
            logging.info(
                f"Using default input sound device index: {self.pa.get_host_api_info_by_index(0)['defaultInputDevice']}")

    def _create_stream(self):
        """Creates a new audio stream from the microphone."""

        def callback(in_data, frame_count, time_info, status):
            self.buffer_queue.put(in_data)
            return (None, pyaudio.paContinue)

        stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.input_rate,
            input=True,
            frames_per_buffer=self.input_rate // self.blocks_per_second,
            stream_callback=callback,
            input_device_index=self.device_index if self.device_index else None
        )
        stream.start_stream()

        return stream

    def _destroy(self):
        """Destroys the stream and terminates recording with PyAudio."""
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()
