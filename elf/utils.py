import struct


def int32_to_bytes(num):
    return struct.pack('I', num)


def int64_to_bytes(num):
    return struct.pack('L', num)


def bytes_to_int32(s):
    return struct.unpack('I', s)[0]


def bytes_to_int64(s):
    return struct.unpack('L', s)[0]


def readfile(filename):
    with open(filename, 'rb') as stream:
        return stream.read()
