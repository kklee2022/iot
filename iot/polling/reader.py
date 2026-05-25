"""Modbus register reader using pymodbus 3.x."""
import logging
import struct
from typing import Dict, Tuple

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

from ..models import Device, RegisterMap

logger = logging.getLogger(__name__)

# Number of 16-bit words consumed by each data type.
_REGISTER_COUNT: Dict[str, int] = {
    "bool": 1,
    "int16": 1,
    "uint16": 1,
    "int32": 2,
    "uint32": 2,
    "float32": 2,
}


def decode_value(registers: list, data_type: str) -> float:
    """Decode a list of 16-bit register words into a Python float."""
    if data_type == "uint16":
        return float(registers[0])
    if data_type == "int16":
        v = registers[0]
        return float(v if v < 0x8000 else v - 0x10000)
    if data_type == "uint32":
        return float((registers[0] << 16) | registers[1])
    if data_type == "int32":
        raw = (registers[0] << 16) | registers[1]
        return float(raw if raw < 0x80000000 else raw - 0x100000000)
    if data_type == "float32":
        packed = struct.pack(">HH", registers[0], registers[1])
        return float(struct.unpack(">f", packed)[0])
    if data_type == "bool":
        return float(bool(registers[0]))
    return float(registers[0])


def read_device_registers(
    device: Device, register_maps
) -> Dict[str, Tuple[float, str]]:
    """
    Open a Modbus TCP connection to *device* and read every enabled register
    in *register_maps*.

    Returns a dict ``{sensor_type: (raw_float, quality_flag)}``.
    quality_flag is ``"good"`` on success or ``"bad"`` on any read error.
    """
    results: Dict[str, Tuple[float, str]] = {}

    client = ModbusTcpClient(host=device.host, port=device.port, timeout=3)

    if not client.connect():
        logger.error(
            "Modbus TCP connect failed: %s (%s:%s)", device.device_id, device.host, device.port
        )
        return {rm.sensor_type: (0.0, "bad") for rm in register_maps}

    try:
        for reg_map in register_maps:
            count = _REGISTER_COUNT.get(reg_map.data_type, 1)
            slave = device.slave_id

            try:
                if reg_map.register_type == RegisterMap.RegisterType.HOLDING:
                    resp = client.read_holding_registers(reg_map.register_address, count, slave=slave)
                elif reg_map.register_type == RegisterMap.RegisterType.INPUT:
                    resp = client.read_input_registers(reg_map.register_address, count, slave=slave)
                elif reg_map.register_type == RegisterMap.RegisterType.COIL:
                    resp = client.read_coils(reg_map.register_address, count, slave=slave)
                elif reg_map.register_type == RegisterMap.RegisterType.DISCRETE:
                    resp = client.read_discrete_inputs(reg_map.register_address, count, slave=slave)
                else:
                    continue

                if resp.isError():
                    logger.warning(
                        "%s/%s: Modbus error response %s",
                        device.device_id, reg_map.sensor_type, resp,
                    )
                    results[reg_map.sensor_type] = (0.0, "bad")
                    continue

                words = resp.registers if hasattr(resp, "registers") else [int(b) for b in resp.bits]
                raw = decode_value(words, reg_map.data_type)
                results[reg_map.sensor_type] = (raw, "good")

            except ModbusException as exc:
                logger.warning(
                    "%s/%s: ModbusException: %s", device.device_id, reg_map.sensor_type, exc
                )
                results[reg_map.sensor_type] = (0.0, "bad")

    except (OSError, ConnectionError) as exc:
        logger.error("Modbus connection error for %s: %s", device.device_id, exc)
        for rm in register_maps:
            results.setdefault(rm.sensor_type, (0.0, "bad"))
    finally:
        client.close()

    return results
