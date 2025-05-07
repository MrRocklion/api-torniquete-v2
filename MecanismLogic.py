import os
import time
import threading
import logging
from dotenv import load_dotenv
from gpiosManagerRaspberry import GpiosManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()  # Esto es para que también salgan por consola
    ]
)

logger = logging.getLogger(__name__)


load_dotenv()
ENVIRONMENT = os.getenv("ENVIRONMENT", "RASPBERRY")
logger.info("Environment: %s", ENVIRONMENT)
doors = GpiosManager()


def normal_door(target_time):
    doors.normal_electromagnet_open()
    doors.open_lock()
    logger.info("ABRIENDO PUERTA ELECTROMAGNETICA")
    start = time.time()
    counter = 0
    while time.time() - start < target_time:
        if doors.ReadSensor():
            while doors.ReadSensor():
                if time.time() - start >= target_time:
                    break
            counter += 1  
        if counter >= 2:
            break
    doors.normal_electromagnet_close()
    doors.close_lock()
    logger.info("COUNTER: %s", counter)
    logger.info("CERRANDO PUERTA ELECTROMAGNETICA")


def special_door():
    doors.special_electromagnet_open()
    time.sleep(10)
    doors.special_electromagnet_close()



class Manager(threading.Thread, GpiosManager):
    def __init__(self, rs232, stop_event):
        super().__init__()
        self.rs232 = rs232
        self.stop_event = stop_event
        # Config tiempos
        self.time_open_normal = 12
        # Estados
        self.activatePass = 0
        self.specialPass = 0

    def run(self):
        while not self.stop_event.is_set():
            with self.rs232.lock:
                if self.activatePass > 0:
                    self._handle_standard_pass()
                elif self.specialPass > 0:
                    self._handle_special_pass()
                elif self.rs232.validation:
                    self.rs232.validation = False
                    self._handle_rs232_pass()
            time.sleep(0.1)

    def _handle_standard_pass(self):
        thread = threading.Thread(target=normal_door, args=(self.time_open_normal,))
        thread.start()
        thread.join()
        self.activatePass = max(0, self.activatePass - 1)

    def _handle_special_pass(self):
        logger.info("Activando pase especial.")
        threading.Thread(target=special_door).start()
        self.specialPass = max(0, self.specialPass - 1)

    def _handle_rs232_pass(self):
        if self.rs232.data[18] != '3':
            thread = threading.Thread(target=normal_door, args=(self.time_open_normal,))
            thread.start()
            thread.join()
        else:
            threading.Thread(target=special_door).start()

    # Métodos públicos
    def generate_pass(self):
        self.activatePass += 1

    def generate_special_pass(self):
        self.specialPass += 1
        return "Pase especial con éxito"

    def read_sensor(self):
        return doors.ReadSensor()

    def test_lock(self):
        return doors.test_lock()

    def test_arrow_light(self):
        return doors.test_arrow()
