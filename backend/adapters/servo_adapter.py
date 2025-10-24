import time


class ServoAdapter:
    """Stub for SG90 treat dispenser control.
    Replace with actual GPIO/serial/PWM implementation as available.
    """
    def __init__(self):
        pass

    def dispense(self, duration_ms: int = 600) -> None:
        # TODO: actuate servo. For now, just sleep to simulate motion.
        time.sleep(max(0, duration_ms) / 1000.0)
