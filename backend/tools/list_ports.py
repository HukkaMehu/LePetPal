from serial.tools import list_ports
for p in list_ports.comports():
    print(f"{p.device}\t{p.description}")
