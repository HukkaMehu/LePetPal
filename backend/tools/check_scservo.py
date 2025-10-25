import sys

print("Python:", sys.version)
try:
    import importlib
    import scservo_sdk as s
    print("scservo_sdk file:", getattr(s, "__file__", "<none>"))
    names = [n for n in dir(s) if ("Packet" in n or "Handler" in n or "Port" in n)]
    print("scservo_sdk attrs:", names)
    # Probe known symbols on root
    has_packet = hasattr(s, "PacketHandler")
    has_port = hasattr(s, "PortHandler")
    print("PacketHandler present (root):", has_packet, "PortHandler present (root):", has_port)
    # Probe common submodule path
    try:
        core = importlib.import_module("scservo_sdk.scservo_sdk")
        print("submodule file:", getattr(core, "__file__", "<none>"))
        names2 = [n for n in dir(core) if ("Packet" in n or "Handler" in n or "Port" in n)]
        print("submodule attrs:", names2)
    except Exception as e:
        print("submodule import failed:", e)
    # Also check feetech_servo_sdk
    try:
        import feetech_servo_sdk as f
        print("feetech_servo_sdk file:", getattr(f, "__file__", "<none>"))
        names3 = [n for n in dir(f) if ("Packet" in n or "Handler" in n or "Port" in n)]
        print("feetech_servo_sdk attrs:", names3)
    except Exception as e:
        print("feetech_servo_sdk import failed:", e)
except Exception as e:
    print("IMPORT ERROR:", e)
    raise
