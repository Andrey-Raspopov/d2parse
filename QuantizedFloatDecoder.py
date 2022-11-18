import math


class QuantizedFloatDecoder:
    def __init__(self, bit_count, flags, low_value, high_value):
        self.low = 0
        self.high = 0
        self.high_low_mul = 0
        self.dec_mul = 0
        self.offset = 0
        self.bit_count = 0
        self.flags = 0
        self.noscale = False

        qff_rounddown = 1 << 0
        qff_roundup = 1 << 1
        qff_encode_zero = 1 << 2
        qff_encode_integers = 1 << 3

        if bit_count == 0 or bit_count >= 32:
            self.noscale = True
            self.bit_count = 32
        else:
            self.noscale = False
            self.bit_count = bit_count
            self.offset = 0.0

            if low_value != 0.0:
                self.low = low_value
            else:
                self.low = 0.0

            if high_value != 0.0:
                self.high = high_value
            else:
                self.high = 1.0

        if flags != 0:
            self.flags = flags
        else:
            self.flags = 0

        self.validate_flags()

        steps = 1 << bit_count

        range_value = 0.0
        if self.flags & qff_rounddown != 0:
            range_value = self.high - self.low
            self.offset = range_value / float(steps)
            self.high -= self.offset
        elif self.flags & qff_roundup != 0:
            range_value = self.high - self.low
            self.offset = range_value / float(steps)
            self.low += self.offset

        if (self.flags & qff_encode_integers) != 0:
            delta = self.high - self.low

            if delta < 1:
                delta = 1

            delta_log2 = math.ceil(math.log(float(delta), 2))
            range_value2 = 1 << int(delta_log2)
            bc = self.bit_count

            while True:
                if (1 << int(bc)) > range_value2:
                    break
                else:
                    bc += 1

            if bc > self.bit_count:
                self.bit_count = bc
                steps = 1 << int(self.bit_count)

            self.offset = float(range_value2) / float(steps)
            self.high = self.low + float(range_value2) - self.offset

        self.high_low_mul = None
        self.dec_mul = None

        self.assign_multipliers(int(steps))

        # print("self.flags & qff_rounddown: ", self.flags & qff_rounddown)
        # print("self.quantize(self.high): ", self.quantize(self.high))
        if self.flags & qff_rounddown != 0:
            if self.quantize(self.low) == self.low:
                self.flags &= ~qff_rounddown

        if self.flags & qff_roundup != 0:
            if self.quantize(self.high) == self.high:
                self.flags &= ~qff_roundup

        if self.flags & qff_encode_zero != 0:
            if self.quantize(0.0) == self.high:
                self.flags &= ~qff_encode_zero

    def quantize(self, val):
        qff_rounddown = 1 << 0
        qff_roundup = 1 << 1
        if val < self.low:
            if self.flags & qff_roundup == 0:
                print("Field tried to quantize an out of range value")
                return

            return self.low
        elif val > self.high:
            if self.flags & qff_rounddown == 0:
                print("Field tried to quantize an out of range value")
                return

            return self.high

        # self.high_low_mul = 512
        i = int((val - self.low) * self.high_low_mul)

        return self.low + (self.high - self.low) * (float(i) * self.dec_mul)

    def assign_multipliers(self, steps):
        self.high_low_mul = 0.0
        range_value = self.high - self.low

        high = 0
        if self.bit_count == 32:
            high = 0xFFFFFFFE
        else:
            high = (1 << self.bit_count) - 1

        high_mul = float(0.0)
        if abs(float(range_value)) <= 0.0:
            high_mul = float(high)
        else:
            high_mul = float(high) / range_value

        if (high_mul * range_value > float(high)) or (float(high_mul - range_value) > float(high)):
            multipliers = [0.9999, 0.99, 0.9, 0.8, 0.7]

            for mult in multipliers:
                high_mul = float(high) / range_value * mult

                if (high_mul * range_value > float(high)) or (float(high_mul * range_value) > float(high)):
                    continue

                break

        self.high_low_mul = high_mul
        self.dec_mul = 1.0 / float(steps - 1)

        if self.high_low_mul == 0.0:
            print("Error computing high / low multiplier")
            return -1

    def validate_flags(self):
        qff_rounddown = 1 << 0
        qff_roundup = 1 << 1
        qff_encode_zero = 1 << 2
        qff_encode_integers = 1 << 3

        if self.flags == 0:
            return -1

        if self.low == 0.0 and (self.flags & qff_rounddown != 0) or (
                self.high == 0.0 and (self.flags & qff_roundup) != 0):
            self.flags &= ~qff_encode_zero

        if self.low == 0.0 and (self.flags & qff_encode_zero != 0):
            self.flags |= ~qff_rounddown
            self.flags &= ~qff_encode_zero

        if self.high == 0.0 and (self.flags & qff_encode_zero != 0):
            self.flags |= ~qff_roundup
            self.flags &= ~qff_encode_zero

        if self.low == 0.0 or self.high < 0.0:
            self.flags &= ~qff_encode_zero

        if self.flags & qff_encode_integers != 0:
            self.flags &= ~(qff_roundup | qff_rounddown | qff_encode_zero)

        if self.flags & (qff_rounddown | qff_roundup) == (qff_rounddown | qff_roundup):
            return -1

    def decode(self, r):
        qff_rounddown = 1 << 0
        qff_roundup = 1 << 1
        qff_encode_zero = 1 << 2
        qff_encode_integers = 1 << 3

        if ((self.flags & qff_rounddown) != 0) and r.read_boolean():
            return self.low
        elif ((self.flags & qff_roundup) != 0) and r.read_boolean():
            return self.high
        elif ((self.flags & qff_encode_zero)) != 0 and r.read_boolean():
            return 0.0
        else:
            return self.low + (self.high - self.low) * float(r.read_bits(self.bit_count)) * self.dec_mul
