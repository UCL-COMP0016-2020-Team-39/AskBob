from askbob.speech.listener.listener import UtteranceService
import wave


class FileUtteranceService(UtteranceService):

    chunk: int = 320

    def __init__(self, filename: str, aggressiveness: int = 1,
                 lowpass_frequency: int = 65, highpass_frequency: int = 4000):
        super().__init__(aggressiveness, lowpass_frequency, highpass_frequency)

        wf = wave.open(filename, 'rb')
        self.input_rate = wf.getframerate()

        if wf.getnchannels() != 1:
            raise RuntimeError(
                "Uploaded WAV files must only have a single audio channel (mono).")

        self.reset_buffer_queue = False
        data = wf.readframes(self.chunk)
        while data:
            self.buffer_queue.put(data)
            data = wf.readframes(self.chunk)

        wf.close()
