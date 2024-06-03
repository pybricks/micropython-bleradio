from bleradio import BLERadio

radio = BLERadio(observe_channels=[5])

old_data = None

while True:

    new_data = radio.observe(5)
    strength = radio.signal_strength(5)

    if new_data == old_data:
        continue

    print(strength, "dBm:", new_data)
    old_data = new_data
