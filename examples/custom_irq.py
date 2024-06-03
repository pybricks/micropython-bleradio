# Basic usage of the radio module, combined with your own BLE handler.

from time import sleep_ms
from bleradio import BLERadio, observe_irq
import bluetooth


def your_ble_irq(event, data):
    # Processes advertising data matching Pybricks scheme, if any.
    channel = observe_irq(event, data)
    if channel is not None:
        # Something was observed on this channel. You could handle this
        # event further here if you like.
        pass

    # Add rest of your conventional BLE handler here.


# Manual control of BLE so you can combine it with other BLE logic.
ble = bluetooth.BLE()
ble.active(True)
ble.irq(your_ble_irq)
ble.gap_scan(0, 30000, 30000)

# Allocate the channels but don't reconfigure BLE.
radio = BLERadio(observe_channels=[4, 18], broadcast_channel=5, ble=ble)

counter = 0

while True:
    # Receive data on channel 4.
    data = radio.observe(4)

    # Broadcast a counter and some constant data.
    radio.broadcast([counter, "hello, world!", 3.14])
    counter += 1

    sleep_ms(100)
