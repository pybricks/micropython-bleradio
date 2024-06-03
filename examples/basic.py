# Basic usage of the radio module.

from time import sleep_ms
from bleradio import BLERadio

# A board can broadcast small amounts of data on one channel. Here we broadcast
# on channel 5. This board will listen for other boards on channels 4 and 18.
radio = BLERadio(broadcast_channel=5, observe_channels=[4, 18])

# You can run a variant of this script on another board, and have it broadcast
# on channel 4 or 18, for example. This board will then receive it.

while True:

    # Data observed on channel 4, as broadcast by another board.
    # It gives None if no data is detected.
    observed = radio.observe(4)
    print(observed)

    # Broadcast some data on our channel, which is 5.
    radio.broadcast(["hello, world!", 3.14])
    sleep_ms(100)
