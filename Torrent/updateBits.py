import sys

def updateBits(value, index):
    mask = 1 << (8 - index) # 7 - (numPart - 1)
    value |= mask

    return value