import serial


class Serial:

    def __init__(self, baudrate, port):
        self.baudrate = baudrate
        self.port = port

        self.ser = serial.Serial()
        self.ser.baudrate = self.baudrate
        self.ser.port = self.port


    def _serial_ports(self):
        """
        Lists every COM port available on the system.

        :return: List of strings
        """

        ports = ['COM%s' % (i + 1) for i in range(256)]

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException) as e:
                pass
        return result


    def serialWrite(self, string: str, size: int = None):
        if self.port not in self._serial_ports():
            raise serial.SerialException(f"Make sure this COM Port exists.")

        try:
            self.ser.open()
        except serial.SerialException as e:
            self.ser.close()

            if "PermissionError" in e.args[0]:
                raise serial.SerialException(f"{e}. Make sure this COM Port isn't already in use.")

            else:
                raise serial.SerialException(e)
        else:
            encodedString = string.encode()
            bytes = self.ser.write(encodedString)

            if bytes != len(encodedString):
                self.ser.close()
                raise serial.SerialException(f"Write operation failed!")

            if size:
                feedback = self.ser.read(size)
            else:
                feedback = self.ser.read(len(encodedString))
            self.ser.close()

            return feedback

    def serialRead(self, size: int = 1):
        if self.port not in self._serial_ports():
            raise serial.SerialException(f"Make sure this COM Port exists.")

        try:
            self.ser.open()
        except serial.SerialException as e:
            self.ser.close()

            if "PermissionError" in e.args[0]:
                raise serial.SerialException(f"{e}. Make sure this COM Port isn't already in use.")

            else:
                raise serial.SerialException(e)

        try:
            result = self.ser.read(size)
        except serial.SerialException as e:
            self.ser.close()
            raise serial.SerialException("Read operation failed!")

        self.ser.close()

        return result


