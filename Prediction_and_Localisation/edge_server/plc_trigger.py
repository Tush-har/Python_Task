

from pyModbusTCP.client import ModbusClient

from utils  import CacheHelper
modbus_client = ModbusClient(host='192.168.1.10', port=502, auto_open=True)