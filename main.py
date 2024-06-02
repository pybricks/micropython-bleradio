# from time import sleep_ms
# from pybricks import PybricksRadio

# radio = PybricksRadio(observe_channels=[4, 18])

# while True:

#     print(radio.observe(4))
#     sleep_ms(100)


from time import sleep_ms
from pybricks import PybricksRadio, pybricks_observe_irq
import bluetooth


def your_ble_irq(event, data):
    # Processes advertising data matching Pybricks scheme, if any.
    pybricks_observe_irq(event, data)

    # Add rest if your BLE handler here.


# Allocate the channels but don't start scanning.
radio = PybricksRadio(observe_channels=[4, 18], start_ble=False)

# Manual control of BLE so you can combine it with other BLE logic.
ble = bluetooth.BLE()
ble.active(True)
ble.irq(your_ble_irq)
ble.gap_scan(0, 30000, 30000)


while True:
    print(radio.observe(4))
    sleep_ms(100)
