#!/usr/bin/env python3
"""Control Fronius Symo GEN24 battery charging via SunSpec Model 124 Modbus TCP."""

import argparse
import socket
import struct
import sys


class ModbusClient:
    """Minimal pure-Python Modbus TCP client for SunSpec register reads/writes."""

    def __init__(self, host: str, port: int = 502, unit_id: int = 1, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.timeout = timeout
        self.tx_id = 0
        self.sock = socket.create_connection((host, port), timeout)

    def close(self) -> None:
        self.sock.close()

    def _recv_exact(self, n: int) -> bytes:
        buf = bytearray()
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("Unexpected EOF from Modbus server")
            buf.extend(chunk)
        return bytes(buf)

    def read_holding_registers(self, addr: int, count: int) -> tuple[int, ...]:
        self.tx_id = (self.tx_id + 1) & 0xFFFF or 1
        req = struct.pack(">HHHBBHH", self.tx_id, 0, 6, self.unit_id, 3, addr, count)
        self.sock.sendall(req)
        mbap = self._recv_exact(7)
        rx_tx, _proto, length, _unit = struct.unpack(">HHHB", mbap)
        pdu = self._recv_exact(length - 1)
        if rx_tx != self.tx_id:
            raise ValueError(f"Transaction ID mismatch: expected {self.tx_id}, got {rx_tx}")
        func = pdu[0]
        if func & 0x80:
            raise RuntimeError(f"Modbus read exception 0x{pdu[1]:02X} at addr {addr}")
        byte_count = pdu[1]
        if byte_count != count * 2:
            raise ValueError(f"Expected {count * 2} bytes, got {byte_count}")
        return struct.unpack(">" + "H" * count, pdu[2:])

    def write_single_register(self, addr: int, value: int) -> None:
        self.tx_id = (self.tx_id + 1) & 0xFFFF or 1
        val_u16 = value & 0xFFFF
        req = struct.pack(">HHHBBHH", self.tx_id, 0, 6, self.unit_id, 6, addr, val_u16)
        self.sock.sendall(req)
        mbap = self._recv_exact(7)
        rx_tx, _proto, length, _unit = struct.unpack(">HHHB", mbap)
        pdu = self._recv_exact(length - 1)
        if rx_tx != self.tx_id:
            raise ValueError(f"Transaction ID mismatch: expected {self.tx_id}, got {rx_tx}")
        func = pdu[0]
        if func & 0x80:
            raise RuntimeError(f"Modbus write exception 0x{pdu[1]:02X} at addr {addr} val {val_u16}")


def set_battery_charge(ip: str, watts: int, port: int = 502, unit_id: int = 1) -> None:
    """Apply forced charge power in watts (<=0 restores normal self-consumption)."""
    # SunSpec Model 124 base at 40343 (int+SF verified on GEN24)
    reg_model_id = 40343
    reg_wchamax = 40345
    reg_storctl_mod = 40348
    reg_outwrte = 40355
    reg_inwrte = 40356
    reg_rvrttms = 40358
    reg_chagriset = 40360

    client = ModbusClient(ip, port=port, unit_id=unit_id)
    try:
        model_id = client.read_holding_registers(reg_model_id, 1)[0]
        if model_id != 124:
            raise RuntimeError(f"Expected SunSpec Model 124 at {reg_model_id}, got {model_id}")

        wchamax = client.read_holding_registers(reg_wchamax, 1)[0]
        if wchamax <= 0:
            raise RuntimeError(f"Invalid WChaMax value {wchamax} at {reg_wchamax}")

        if watts <= 0:
            client.write_single_register(reg_storctl_mod, 0)
            client.write_single_register(reg_outwrte, 10000)
            client.write_single_register(reg_rvrttms, 0)
            print(f"Reset {ip} to automatic self-consumption (StorCtl_Mod=0, OutWRte=10000, WChaMax={wchamax}W)")
            return

        target_w = min(watts, 4800, wchamax)
        pct_x100 = max(-10000, min(0, -int(round((target_w / wchamax) * 10000))))
        raw_out = (65536 + pct_x100) & 0xFFFF

        client.write_single_register(reg_chagriset, 1)
        client.write_single_register(reg_inwrte, 10000)
        client.write_single_register(reg_outwrte, raw_out)
        client.write_single_register(reg_rvrttms, 120)
        client.write_single_register(reg_storctl_mod, 2)
        print(
            f"Set {ip} forced charge: target={target_w}W "
            f"(WChaMax={wchamax}W, OutWRte={pct_x100}, raw={raw_out}, StorCtl_Mod=2, RvrtTms=120s)"
        )
    finally:
        client.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Fronius GEN24 EEG battery Modbus controller")
    parser.add_argument("--ip", required=True, help="Fronius GEN24 IP address")
    parser.add_argument("--watts", required=True, type=int, help="Target charge watts (<=0 to reset)")
    parser.add_argument("--port", type=int, default=502)
    parser.add_argument("--unit-id", type=int, default=1)
    args = parser.parse_args()
    set_battery_charge(args.ip, args.watts, port=args.port, unit_id=args.unit_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
