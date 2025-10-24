import time


class TTSSpeaker:
    def speak(self, text: str) -> None:
        if not text:
            return
        time.sleep(0.1)
