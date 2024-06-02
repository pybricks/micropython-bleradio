# from time import sleep_ms
# from pybricks import PybricksRadio

# radio = PybricksRadio(broadcast_channel=5, observe_channels=[4, 18])

# while True:
#     observed = radio.observe(4)
#     print(observed)
#     radio.broadcast(["hello, world!", 3.14])
#     sleep_ms(100)


from time import sleep_ms
from pybricks import PybricksRadio, pybricks_observe_irq
import bluetooth


def your_ble_irq(event, data):
    # Processes advertising data matching Pybricks scheme, if any.
    pybricks_observe_irq(event, data)

    # Add rest if your BLE handler here.


# Manual control of BLE so you can combine it with other BLE logic.
ble = bluetooth.BLE()
ble.active(True)
ble.irq(your_ble_irq)
ble.gap_scan(0, 30000, 30000)

# Allocate the channels but don't start scanning.
radio = PybricksRadio(observe_channels=[4, 18], broadcast_channel=5, ble=ble)


while True:

    data = radio.observe(4)

    radio.broadcast(data)
    sleep_ms(100)
