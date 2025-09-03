###############################################################################
# Much of this seems dependent on router specific addressing
# TODO: Generalize once working with hardware
###############################################################################

# RD200

import asyncio
from bleak import BleakScanner, BleakClient, BleakGATTCharacteristic
import time

LBS_UUID_CONTROL = "00001524-1212-efde-1523-785feabcd123"
LBS_UUID_LOG = "00001526-1212-efde-1523-785feabcd123"
LBS_UUID_MEAS = "00001525-1212-efde-1523-785feabcd123"
LBS_UUID_SERVICE = "00001523-1212-efde-1523-785feabcd123"

data = b'\x50\x11\x00\x00\x00\x00\x00\x00 \
                    \x00\x00\x00\x00\x00\x00 \
                    \x00\x00\x00\x00\x00\x00'
address = "F5:26:EA:EF:B7:15"


async def read_radon():
    client = BleakClient(address)
    try:
        await client.connect()
        # print(f"{await client.read_gatt_char(LBS_UUID_CONTROL)}")
        # print(f"{await client.read_gatt_char(LBS_UUID_LOG)}")

        await client.write_gatt_char(LBS_UUID_CONTROL, data)
        measurement = await client.read_gatt_char(LBS_UUID_MEAS)
        # print(int.from_bytes(measurement[2:4],"little")/37)
        return int.from_bytes(measurement[2:4], "little")/37
    except Exception as e:
        print(e)
    finally:
        await client.disconnect()


''''
this.calMeas_pCi = ((float) Math.round(
                            (((float) mDevice.ResultData.valueNow)
                            / 37.0f) * 100.0f))
                    / 100.0f;


scan over attributes
see which one matches LBS_UUID_MEAS
record its handle
write to LBS_UUID_CONTROL
listen to meas handle
parse as bq/m^3 and convert to pci/l
set notify request on that handle
'''
