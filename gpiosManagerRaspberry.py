import os
from gpiozero import Device
from gpiozero import DigitalOutputDevice, DigitalInputDevice
from dotenv import load_dotenv

load_dotenv()

# Detecta entorno desde .env
ENV = os.getenv("TARGET", "PI3")

if ENV == "PI5":
    try:
        from gpiozero.pins.lgpio import LGPIOFactory
        Device.pin_factory = LGPIOFactory()
        print("Usando LGPIOFactory (Raspberry Pi 5)")
    except Exception as e:
        from gpiozero.pins.pigpio import PiGPIOFactory
        Device.pin_factory = PiGPIOFactory()
        print("Fallo LGPIO, usando PiGPIOFactory como respaldo:", e)
else:
    from gpiozero.pins.rpigpio import RPiGPIOFactory
    Device.pin_factory = RPiGPIOFactory()
    print("Usando RPiGPIOFactory (Raspberry Pi 3)")

import time


class GpiosManager():
    def __init__(self):
        # Pines de salida
        self.normal_electromagnet = DigitalOutputDevice(6)
        self.special_electromagnet = DigitalOutputDevice(26)
        self.lock = DigitalOutputDevice(18)
        self.arrowLight = DigitalOutputDevice(23)

        # Pines de entrada
        self.sensor = DigitalInputDevice(22, pull_up=True)
        self.pulsante = DigitalInputDevice(2,pull_up=True)
        #estado inicial de pines
        self.normal_electromagnet.on()
        self.special_electromagnet.on()
        self.lock.on()
        self.arrowLight.on()


    def normal_electromagnet_open(self):
        self.normal_electromagnet.off()
        self.arrowLight.off()
        return "Cerradura Magnetica Puerta Normal abierta"

    def normal_electromagnet_close(self):
        self.normal_electromagnet.on()
        self.arrowLight.on()
        return "Cerradura Magenitca Puerta Normal bloqueada"
    
    def special_electromagnet_open(self):
        self.special_electromagnet.off()
        self.arrowLight.off()
        return "Cerradura Magnetica Puerta Especial Abierta"

    def special_electromagnet_close(self):
        self.special_electromagnet.on()
        self.arrowLight.on()
        return "Cerradura Magnetica Puerta Especial Cerrada"

    def open_lock(self):
        self.lock.off()

    def close_lock(self):
        self.lock.on()

    def test_lock(self):
        self.lock.off()
        time.sleep(1)
        self.lock.on()

    def test_arrow(self):
        self.arrowLight.off()
        time.sleep(1)
        self.arrowLight.on()
        return 'Luz Led testeada con exito'

    def read_sensor(self):
        return self.sensor.value == 0


