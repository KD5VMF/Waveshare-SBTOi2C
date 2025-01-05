import ctypes
import os
import time

os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console screen at the beginning

# Load the Windows DLL for the CH347 device
dll_path = os.path.join(os.getcwd(), 'CH347DLLA64.DLL')  # Ensure the correct path
ch347_dll = ctypes.windll.LoadLibrary(dll_path)

# Define argument types and return types for the DLL functions
ch347_dll.CH347OpenDevice.argtypes = [ctypes.c_uint]
ch347_dll.CH347OpenDevice.restype = ctypes.c_int

ch347_dll.CH347CloseDevice.argtypes = [ctypes.c_uint]
ch347_dll.CH347CloseDevice.restype = None

ch347_dll.CH347StreamI2C.argtypes = [
    ctypes.c_uint, ctypes.c_uint,
    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_uint,
    ctypes.POINTER(ctypes.c_ubyte)
]
ch347_dll.CH347StreamI2C.restype = ctypes.c_int

ch347_dll.CH347StreamI2C_RetACK.argtypes = [
    ctypes.c_uint, 
    ctypes.c_uint,
    ctypes.POINTER(ctypes.c_ubyte), 
    ctypes.c_uint,
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.POINTER(ctypes.c_uint),
]
ch347_dll.CH347StreamI2C_RetACK.restype = ctypes.c_bool
    
class USBI2C:
    def __init__(self, usb_dev_index=0):
        self.dev_index = usb_dev_index
        self.open_device()

    def open_device(self):
        self.handle = ch347_dll.CH347OpenDevice(self.dev_index)
        if self.handle != -1:
            print(f"Opened device at index: {self.dev_index}")
        else:
            raise Exception("USB CH347 Open Failed!")

    def close_device(self):
        if self.handle != -1:
            ch347_dll.CH347CloseDevice(self.dev_index)
            print(f"Closed device at index: {self.dev_index}")

    def read_dht12(self):
            address=0x5c
            write_buffer = (ctypes.c_ubyte * 2)(address << 1,0x00)  # Address as 7-bit write address
            read_buffer = (ctypes.c_ubyte * 5)()
            ack_num = ctypes.c_ulong()
            # Attempt to write a dummy command to see if the device acknowledges
            result = ch347_dll.CH347StreamI2C_RetACK(self.dev_index, 2, write_buffer, 5, read_buffer , ctypes.byref(ack_num))
            # 校验数据
            if (result != 1) :
                return None, None, None, None
            if ((read_buffer[0] + read_buffer[1] +read_buffer[2]+read_buffer[3]) & 0xFF == read_buffer[4]):
                return read_buffer[0],read_buffer[1],read_buffer[2],read_buffer[3]
            else:
                return None, None, None, None


def main():
    # Initialize the I2C device
    i2c_device = USBI2C(usb_dev_index=0)  # Adjust the index if necessary
    while True:
        try:
            time.sleep(2)  # 等待2秒再次读取
            hum1, hum2,temp1 ,temp2 = i2c_device.read_dht12()
            if hum1 is not None and temp1 is not None and hum2 is not None and temp2 is not None:     
                print("湿度: %d.%d " % (hum1, hum2), end=' ')
                print("温度: %d.%d ℃" % (temp1, temp2))
            else:
                print("读取失败")
                break
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    i2c_device.close_device()


if __name__ == "__main__":
    main()
