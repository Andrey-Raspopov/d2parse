import math
import struct

import numpy as np
import snappy


class FileReader(object):
    """
    Some utilities to make it a bit easier to read values out of the .dem file
    """

    def __init__(self, stream):
        self.stream = stream
        stream.seek(0, 2)
        self.size = stream.tell()
        self.remaining = self.size
        stream.seek(0)

        self.pos = 0
        self.bit_count = 0
        self.bit_val = 0

    def more(self):
        return self.remaining > 0

    def nibble(self, length):
        self.remaining -= length
        if self.remaining < 0:
            raise ValueError("Not enough data")

    def read_byte(self):
        self.nibble(1)

        return ord(self.stream.read(1))

    def read(self, length=None):
        if length is None:
            length = self.remaining

        self.nibble(length)

        return self.stream.read(length)

    def read_int32(self):
        self.nibble(4)

        return struct.unpack("i", self.stream.read(4))[0]

    def read_uint32(self):
        self.nibble(4)

        return struct.unpack("I", self.stream.read(4))[0]

    def read_boolean(self):
        return self.read_bits(1) == 1

    def next_byte(self):
        self.pos += 1
        if self.pos > self.size:
            print('nextByte: insufficient buffer ({} of {})'.format(self.pos, self.size))

        value = self.stream.read(1)
        value = ord(value)

        return value

    def read_byte_test(self):
        if self.bit_count == 0:
            return self.next_byte()

        return self.read_bits(8)

    def read_bytes(self, n):
        buf = bytearray()
        for i in range(n):
            data = self.read_bits(8)
            buf.extend(bytes([data]))

        return bytes(buf)

    def read_bits(self, n):
        while n > self.bit_count:
            nextByte = self.next_byte()
            self.bit_val |= nextByte << self.bit_count
            self.bit_count += 8

        x = (self.bit_val & ((1 << n) - 1))
        self.bit_val >>= n
        self.bit_count -= n

        return x

    def read_ubit_var_fp(self):
        if self.read_boolean():
            return self.read_bits(2)

        if self.read_boolean():
            return self.read_bits(4)

        if self.read_boolean():
            return self.read_bits(10)

        if self.read_boolean():
            return self.read_bits(17)

        return self.read_bits(31)

    def read_ubit_var_field_path(self):
        return int(self.read_ubit_var_fp())

    def read_string(self):
        buf = bytearray()
        while True:
            b = bytes([self.read_byte_test()])
            if b == b'\x00':
                break

            buf.extend(b)

        return bytes(buf)

    def read_vint32(self):
        """
        This seems to be a variable length integer ala utf-8 style
        """
        result = 0
        count = 0
        while True:
            if count > 4:
                raise ValueError("Corrupt VarInt32")

            b = self.read_byte()
            result = result | (b & 0x7F) << (7 * count)
            count += 1

            if not b & 0x80:
                return result

    def read_var_uint32(self):
        x = np.uint32(0)
        s = np.uint32(0)
        while True:
            b = np.uint32(self.read_byte_test())

            x |= (b & 0x7F) << s
            s += 7

            if ((b & 0x80) == 0) or (s == 35):
                break

        return x

    def read_var_uint64(self):
        x = 0
        s = 0
        i = 0
        while True:
            b = self.read_byte_test()
            if b < 0x80:
                if i > 9 or i == 9 and b > 1:
                    break

                return x | (int(b) << s)

            x |= int(b & 0x7f) << s
            s += 7

            i += 1

    def read_var_int32(self):
        ux = self.read_var_uint32()
        x = np.int32(ux >> 1)
        if ux & 1 != 0:
            x = ~x

        return x

    def read_ubit_var(self):
        index = self.read_bits(6)

        flag = index & 0x30
        if flag == 16:
            index = (index & 15) | (self.read_bits(4) << 4)
        elif flag == 32:
            index = (index & 15) | (self.read_bits(8) << 4)
        elif flag == 48:
            index = (index & 15) | (self.read_bits(28) << 4)

        return index

    def read_coord(self):
        value = 0.0

        intval = self.read_bits(1)
        fractval = self.read_bits(1)
        signbit = False

        if intval != 0 or fractval != 0:
            signbit = self.read_boolean()

            if intval != 0:
                intval = self.read_bits(14) + 1

            if fractval != 0:
                fractval = self.read_bits(5)

            value = float(intval) + float(fractval) * (1.0 / (1 << 5))

            if signbit:
                value = -value

        return value

    def rem_bytes(self):
        return self.size - self.pos

    def read_bits_as_bytes(self, n):
        tmp = bytearray()
        while n >= 8:
            read_value = self.read_byte_test()
            tmp.extend(bytes([read_value]))
            n -= 8

        if n > 0:
            read_value = self.read_bits(n)
            # read_value_byte = bytes(read_value)
            tmp.extend(bytes([read_value]))

        return bytes(tmp)

    def read_normal(self):
        is_neg = self.read_boolean()
        len = self.read_bits(11)
        ret = float(len) * float(1.0 / (float(1 << 11) - 1.0))

        if is_neg:
            return -ret
        else:
            return ret

    def read_3bit_normal(self):
        ret = [0.0, 0.0, 0.0]

        hasX = self.read_boolean()
        hasY = self.read_boolean()

        if hasX:
            ret[0] = self.read_normal()

        if hasY:
            ret[1] = self.read_normal()

        negZ = self.read_boolean()
        prodsum = ret[0] * ret[0] + ret[1] * ret[1]

        if prodsum < 1.0:
            ret[2] = float(math.sqrt(float(1.0 - prodsum)))
        else:
            ret[2] = 0.0

        if negZ:
            ret[2] = -ret[2]

        return ret

    def read_le_uint64(self):
        result = self.read_bytes(8)
        result = int.from_bytes(result, byteorder='little')
        # print("result: ", result)

        return result

    def read_angle(self, n):
        result = self.read_bits(n)
        result = float(result) * 360 / float(int(1 << n))

        return result

    def read_message(self, message_type, compressed=False, read_size=True):
        """
        Read a protobuf message
        """
        if read_size:
            size = self.read_vint32()
            b = self.read(size)
        else:
            b = self.read()

        if compressed:
            b = snappy.decompress(b)

        m = message_type()
        m.ParseFromString(b)

        return m, b
