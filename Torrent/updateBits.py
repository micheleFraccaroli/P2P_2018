import sys

def updateBits(value, index):
    mask = 1 << (8 - index) # 7 - (numPart - 1)
    value |= mask
    print("mask ---> " + str("{:08b}".format(mask)))

    return value

if __name__ == "__main__":
    value = 31
    index = 2

    v = updateBits(value, index)
    print("value ---> " + str("{:08b}".format(value)))
    print(str("{:08b}".format(v)))