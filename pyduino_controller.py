import serial.tools.list_ports
import time

DEFAULT_PORT = "/dev/cu.usbserial-14230"


class PyduinoController:
    def __init__(self, port=DEFAULT_PORT, baud_rate=115200):
        try:
            self.arduino = serial.Serial(port, baud_rate)
        except serial.SerialException:
            print(f"Failed to connect to Arduino on port {port}")
            print("Available serial ports:")
            ports = serial.tools.list_ports.comports()
            for port in ports:
                print(port.device)
            self.arduino = None

        time.sleep(2)  # Wait for the connection to establish

    def send_command(self, command):
        if self.arduino is None:
            return

        self.arduino.write(command.encode('utf-8'))  # Encode to bytes
        # time.sleep(0.05)  # Add a small delay to allow the Arduino to process the command
        if self.arduino.in_waiting > 0:
            response = self.arduino.readline().decode('utf-8').strip()
            print(f"Received: {response}")

    def close(self):
        if self.arduino is None:
            return
        self.arduino.close()

if __name__ == "__main__":

    arduino_controller = PyduinoController()
    print(arduino_controller.send_command("L"))

    # print("Sending commands to Arduino")
    # commands = ["R", "L", "U", "D", "F"]
    # for command in commands:
    #     arduino_controller.send_command(command)
    #     print(f"Sent: {command}")
    #     time.sleep(2)  # Wait for 1 second
    #
    # arduino_controller.close()
