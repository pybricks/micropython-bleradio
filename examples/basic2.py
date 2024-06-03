from bleradio import BLERadio

radio = BLERadio(observe_channels=[5])

old_data = None

while True:

    new_data = radio.observe(5)
    if new_data != old_data:
        print(new_data)
        old_data = new_data
