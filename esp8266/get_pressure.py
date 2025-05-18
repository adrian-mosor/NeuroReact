import serial
import time

# Configure serial port (match baud rate from ESP8266 sketch)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

print("Reading pressure values from /dev/ttyUSB0...\n(Press Ctrl+C to stop)")

try:
    while True:
        line = ser.readline().decode().strip()
        if line.isdigit():
            pressure = int(line)
            print(f"Pressure: {pressure}")
        time.sleep(0.1)  # Optional: prevent excessive CPU usage
except KeyboardInterrupt:
    print("\nStopped by user.")
finally:
    ser.close()

