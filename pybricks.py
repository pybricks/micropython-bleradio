from micropython import const
from time import ticks_ms
import bluetooth
from struct import pack_into, unpack


_IRQ_SCAN_RESULT = const(5)

_LEGO_ID_MSB = const(0x03)
_LEGO_ID_LSB = const(0x97)
_MANUFACTURER_DATA = const(0xFF)

_DURATION = const(0)
_INTERVAL_US = const(30000)
_WINDOW_US = const(30000)
_RSSI_FILTER_WINDOW_MS = const(512)
_OBSERVED_DATA_TIMEOUT_MS = const(1000)
_RSSI_MIN = const(-128)

_ADVERTISING_OBJECT_SINGLE = const(0x00)
_ADVERTISING_OBJECT_TRUE = const(0x01)
_ADVERTISING_OBJECT_FALSE = const(0x02)
_ADVERTISING_OBJECT_INT = const(0x03)
_ADVERTISING_OBJECT_FLOAT = const(0x04)
_ADVERTISING_OBJECT_STRING = const(0x05)
_ADVERTISING_OBJECT_BYTES = const(0x06)

_ADV_MAX_SIZE = const(31)
_ADV_HEADER_SIZE = const(5)
_ADV_COPY_FMT = const("31s")

_LEN = const(0)
_DATA = const(1)
_TIME = const(2)
_RSSI = const(3)

INT_FORMATS = {
    1: "b",
    2: "h",
    4: "i",
}

observed_data = {}


def pybricks_observe_irq(event, data):
    if event == _IRQ_SCAN_RESULT:
        addr_type, addr, adv_type, rssi, adv_data = data

        # Analyze only advertisements matching Pybricks scheme.
        if (
            len(adv_data) <= _ADV_HEADER_SIZE
            or adv_data[1] != _MANUFACTURER_DATA
            or adv_data[2] != _LEGO_ID_LSB
            or adv_data[3] != _LEGO_ID_MSB
        ):
            return

        # Get channel buffer, if allocated.
        channel = adv_data[4]
        if channel not in observed_data:
            return
        info = observed_data[channel]

        # Update time interval.
        diff = ticks_ms() - info[_TIME]
        info[_TIME] += diff
        if diff > _RSSI_FILTER_WINDOW_MS:
            diff = _RSSI_FILTER_WINDOW_MS

        # Approximate a slow moving average to make RSSI more stable.
        info[_RSSI] = (
            info[_RSSI] * (_RSSI_FILTER_WINDOW_MS - diff) + rssi * diff
        ) // _RSSI_FILTER_WINDOW_MS

        # Copy advertising data without allocation.
        info[_LEN] = len(adv_data) - _ADV_HEADER_SIZE
        pack_into(_ADV_COPY_FMT, info[_DATA], 0, adv_data)


def get_data_info(info_byte: int):
    data_type = info_byte >> 5
    data_length = info_byte & 0x1F
    return data_type, data_length


def unpack_one(data_type: int, data: memoryview):
    if data_type == _ADVERTISING_OBJECT_TRUE:
        return True
    elif data_type == _ADVERTISING_OBJECT_FALSE:
        return False
    elif data_type == _ADVERTISING_OBJECT_SINGLE:
        return None

    # Remaining types require data.
    if len(data) == 0:
        return None

    elif data_type == _ADVERTISING_OBJECT_INT and len(data) in INT_FORMATS:
        return unpack(INT_FORMATS[len(data)], data)[0]
    elif data_type == _ADVERTISING_OBJECT_FLOAT:
        return unpack("f", data)[0]
    elif data_type == _ADVERTISING_OBJECT_STRING:
        return data.decode("utf-8")
    elif data_type == _ADVERTISING_OBJECT_BYTES:
        return data
    else:
        return None


def decode(data: memoryview):
    first_type, _ = get_data_info(data[0])

    # Case of one value instead of tuple.
    if first_type == _ADVERTISING_OBJECT_SINGLE:
        # Only proceed if this has some data.
        if len(data) < 2:
            return None

        value_type, value_length = get_data_info(data[1])
        return unpack_one(value_type, data[2 : 2 + value_length])

    # Unpack iteratively.
    unpacked = []
    index = 0

    while index < len(data):
        data_type, data_length = get_data_info(data[index])

        # Check if there is enough data left.
        if index + 1 + data_length > len(data):
            break

        # Unpack the value.
        data_value = data[index + 1 : index + 1 + data_length]
        unpacked.append(unpack_one(data_type, data_value))
        index += 1 + data_length

    return unpacked


class PybricksRadio:

    def __init__(self, broadcast_channel: int = 0, observe_channels=[], ble=None):
        global observed_data
        observed_data = {
            ch: [0, bytearray(_ADV_MAX_SIZE), 0, _RSSI_MIN] for ch in observe_channels
        }

        if ble is None:
            # BLE not given, so initialize our own instance.
            self.ble = bluetooth.BLE()
            self.ble.active(True)
            self.ble.irq(pybricks_observe_irq)
            self.ble.gap_scan(_DURATION, _INTERVAL_US, _WINDOW_US)
        else:
            # Use externally provided BLE, configured and
            # controlled by user.
            self.ble = ble

    def observe(self, channel: int):
        if channel not in observed_data:
            return None

        info = observed_data[channel]

        if ticks_ms() - info[_TIME] > _OBSERVED_DATA_TIMEOUT_MS:
            info[_RSSI] = _RSSI_MIN

        if info[_RSSI] == _RSSI_MIN:
            return None

        data = memoryview(info[_DATA])
        return decode(data[_ADV_HEADER_SIZE : info[_LEN] + _ADV_HEADER_SIZE])
