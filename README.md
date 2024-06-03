# Connectionless messaging via Bluetooth Low Energy (BLE) with MicroPython

This MicroPython library allows boards with BLE to broadcast (advertise) and
observe (scan) small amounts of data without setting up any connections.

This allows very simple many-to-many communication between broadcasters
and multiple observers. Each board can broadcast on one channel (0-255), and
observer on multiple channels.

The starting order does not matter, and you can add or remove boards to and
from the network as you go.

It matches the protocol used on LEGO hubs that run Pybricks. This means you
can also communicate with these LEGO hubs from any MicroPython board with BLE.

## What can you send and receive?

You can send signed integer values, floating point numbers, booleans, strings,
or bytes. Or a list/tuple of these objects.

For example, you can broadcast one of the following:

```python

data = 12345

data = "Hello, world!"

data = b"\x01\x02\x03"

data = (123, 3.14, True, "Hello World")
```

Boolean values are packed into one byte. All other types are packed into their
respective sizes plus one byte for the type.

Since advertisements payloads are limited to 31 bytes by the Bluetooth spec and
there are 5 bytes of overhead, the combined size of all type headers and values
is limited to 26 bytes.

When no data is observed, the `observe` method returns `None`.

To stop broadcasting, use `broadcast(None)`.

The full specification is available in the [protocol](https://github.com/pybricks/technical-info/blob/master/pybricks-ble-broadcast-observe.md) file.

## States versus events

Due to the nature of communication, this technique works best for sending
_states_, not _events_. Values are broadcast all the time until you change the
data, but there is no guarantee that one single value will be received.

For example, if you want to use a button to incrementally turn a motor by 90
degrees, you should not broadcast a message for each button press. Instead, you could
maintain the target angle on the broadcaster, and broadcast `90`, `180`, `270`,
and so on, incrementing every time the button is pressed.

## Installation

Copy [bleradio.py](https://raw.githubusercontent.com/pybricks/micropython-bleradio/master/bleradio.py) to your board manually.

Or use the `mpremote` tool to install it directly from GitHub:

```
mpremote mip install https://raw.githubusercontent.com/pybricks/micropython-bleradio/master/bleradio.py
```

## Example (run this one one board...)

```python
# Basic usage of the radio module.

from time import sleep_ms
from bleradio import BLERadio

# A board can broadcast small amounts of data on one channel. Here we broadcast
# on channel 5. This board will listen for other boards on channels 4 and 18.
radio = BLERadio(broadcast_channel=5, observe_channels=[4, 18])

# You can run a variant of this script on another board, and have it broadcast
# on channel 4 or 18, for example. This board will then receive it.

counter = 0

while True:

    # Data observed on channel 4, as broadcast by another board.
    # It gives None if no data is detected.
    observed = radio.observe(4)
    print(observed)

    # Broadcast some data on our channel, which is 5.
    radio.broadcast(["hello, world!", 3.14, counter])
    counter += 1
    sleep_ms(100)
```

## Example (... run this on any number of other boards)

```python
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
```

## Mixing it with other BLE code

See [examples/custom_irq](examples/custom_irq.py) to see how you can set up the
observe IRQ manually so you can mix it with other BLE code.

## Mixing it with LEGO Hubs that run Pybricks

You can use this library to communicate with LEGO hubs that run Pybricks. For
example, you can use a MicroPython board to control a LEGO hub.

Hubs running Pybricks already have this functionality built in so you won't
need to install this library on those hubs. The API is mostly the same, but the
channels are specified [during hub
setup](https://docs.pybricks.com/en/latest/hubs/primehub.html).

See [this video for an example](https://www.youtube.com/watch?v=WzmcihSV2YE).
Any hub shown here could be replaced by a MicroPython board with BLE.

## Local development

If you use `vscode`, run the build task (`Ctrl+Shift+B`) to automatically
upload the local library to the board and then run the currently open example.
This method requires `mpremote`.

## Contributing

You can use the library as shown [here](./LICENSE), but we kindly ask you to
suggest changes to the protocol here in an issue so we don't end up with too
many incompatible versions.
