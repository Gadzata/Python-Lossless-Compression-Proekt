import sys
from struct import *

if __name__ == '__main__':

    pocetenFile, n = "demofile.txt", 128
    string = ""
    maxSize = pow(2, int(n))

    file = open(pocetenFile)
    data = file.read()

    dataComp = []
    dictSize, dictChar = 256, {chr(i): i for i in range(256)}

    for charNext in data:
        stringChar = string + charNext

        if stringChar in dictChar:
            string = stringChar

        else:
            dataComp.append(dictChar[string])

            if len(dictChar) <= maxSize:
                dictChar[stringChar] = dictSize
                dictSize += 1

            string = charNext

    if string in dictChar:
        dataComp.append(dictChar[string])

    out = pocetenFile.split(".")[0]
    krajenFile = open(out + ".lzw", "wb")

    for data in dataComp:
        krajenFile.write(pack('>H', int(data)))

    krajenFile.close()
    file.close()
