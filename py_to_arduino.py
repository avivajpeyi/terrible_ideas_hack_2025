import serial
import time
import serial
import time
import serial
import serial.tools.list_ports
import time


ports = serial.tools.list_ports.comports()
print("Available serial ports:")
for port in ports:
    print(port.device)


arduino = serial.Serial('/dev/cu.usbserial-14230', 115200)


def send_command(command):
    arduino.write(command.encode('utf-8'))  # Encode to bytes
    # Add a small delay to allow the Arduino to process the command
    time.sleep(0.05)
    # Read the response from the Arduino
    if arduino.in_waiting > 0:
        response = arduino.readline().decode('utf-8').strip()
        print(f"Received: {response}")



print("Sending commands to Arduino")
for i in range(10):
    send_command("1") # Send command to turn on the LED
    time.sleep(1) # Wait for 1 second
    send_command("0") # Send command to turn off the LED
    time.sleep(1) # Wait for 1 second
    for j in range(5):
        send_command("1")  # Send command to turn on the LED
        time.sleep(0.2)  # Wait for 1 second
        send_command("0")  # Send command to turn off the LED
        time.sleep(0.2)  # Wait for 1 second
