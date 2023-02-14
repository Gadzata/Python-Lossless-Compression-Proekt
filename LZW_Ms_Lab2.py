import cv2
import numpy as np
from collections import Counter


def encodeBase(pixelsImage, blockSize, probsLim, float_type='float64'):
    block = []
    blocks = []
    i = 0

    for pxl in pixelsImage:
        i = i + 1
        block.append(pxl)

        if i % blockSize == 0:
            blocks.append(block)
            block = []

    encodedArray = []
    encodedLim = {}
    start, end, startLog, endLog = 0, 0, 0, 0

    for i in range(len(blocks)):
        start = startLog = probsLim[blocks[i][0]][0]
        end = endLog = probsLim[blocks[i][0]][1]

        for pxl in blocks[i]:
            calc1 = (end - start) * probsLim[pxl][0]
            calc2 = (end - start) * probsLim[pxl][1]
            startLog = start + calc1
            endLog = start + calc2
            start = startLog
            end = endLog

        avg = (start + end) / 2
        tempS = ""

        for j in range(32):
            avg *= 2
            if int(avg) == 1:
                tempS = tempS + "1"
            else:
                tempS = tempS + "0"
            avg = avg - int(avg)

        encodedArray.append(tempS[::-1])
        encodedLim[tempS] = start, end

    encodedArray = np.array(encodedArray)
    np.save("encodedArray.npy", encodedArray)


def decodeBase(encodedName, n, m, blockSize, probsLim, pxlsAdditional):
    encodedArray = np.load(encodedName + ".npy")
    decodedArray = []
    length = encodedArray.shape[0]

    for i in range(length):
        start = startLog = 0
        end = endLog = 1
        encodedNumber = encodedArray[i]
        bag = 0
        for j in range(32):
            if encodedNumber[31 - j] == "1":
                bag = bag + pow(2, -(j + 1))

        for j in range(blockSize):
            keyLn = bag

            if startLog != endLog:
                calc1 = (bag - startLog)
                calc2 = (endLog - startLog)
                keyLn = calc1 / calc2

            probs = 0
            for k in probsLim.keys():
                if (keyLn >= probsLim[k][0]) and (keyLn < probsLim[k][1]):
                    probs = k
                    break

            decodedArray.append(probs)

            startLog = start + (end - start) * probsLim[probs][0]
            endLog = start + (end - start) * probsLim[probs][1]
            start = startLog
            end = endLog

    while pxlsAdditional != 0:
        decodedArray.remove(0)
        pxlsAdditional -= 1

    result = np.array(decodedArray).reshape(n, m)
    cv2.imwrite('result.jpg', result)
    cv2.imshow('result.jpg', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    image = cv2.imread("demoimage.jpg")
    # Goleminata na blockot po default 4, moze da se menuva
    blockSize = 4
    floatType = "float16"

    grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    pixelsImage = np.array(grayImage.flatten())

    pxlsAdditional = 0
    while pixelsImage.shape[0] % blockSize != 0:
        pixelsImage = np.append(pixelsImage, 0)
        pxlsAdditional = pxlsAdditional + 1

    leng = pixelsImage.shape[0]
    freqs = Counter(pixelsImage)
    probs = {}
    for i in freqs.keys():
        probs[i] = freqs[i] / leng

    plat = 0
    probsLim = {}
    for i in probs.keys():
        probsLim[i] = plat, plat + probs[i]
        plat = plat + probs[i]

    np.save("probs.npy", probsLim)
    encodeBase(pixelsImage, blockSize, probsLim)

    n, m = image.shape[0], image.shape[1]
    decodeBase("encodedArray", n, m, blockSize, probsLim, pxlsAdditional)
