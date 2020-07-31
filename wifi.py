#!/usr/bin/python
import sys, getopt
import struct
from PIL import Image

def main(argv):
    inputfile = ''
    width = 0
    height = 0
    outarray = ''
    try:
        opts, args = getopt.getopt(argv,"i:w:h:o:",["ifile=","width=","height","array="])
    except getopt.GetoptError:
        print 'bmp2array.py -i <inputfile> -w <width> -h <height> -o <output array>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-help":
            print 'bmp2array.py -i <inputfile> -w <width> -h <height> -o <output array>'
            sys.exit()
        elif opt in ("-i","--ifile"):
            inputfile = arg
        elif opt in ("-w","--width"):
            width = int(arg)
        elif opt in ("-h","--height"):
            height = int(arg)
        elif opt in ("-o","--array"):
            outarray = arg
    print "input file:",inputfile
    print "width:",width
    print "height:",height
    print "output array name:",outarray

    colorImagereadin = Image.open(inputfile)
    colorImageread = colorImagereadin.rotate(angle = 0)
    #colorImageread = colorImagereadin.transpose(method=Image.FLIP_TOP_BOTTOM)
    #(width,height) = (160,160)
    colorImageresize = colorImageread.resize((width,height))

    # Convert using adaptive palette of color depth 4
    colorImage = colorImageresize.convert("P", palette=Image.ADAPTIVE, colors=4)
    colorImage.save("resize.bmp")

    #Open our input file and dump it into a list of bytes
    infile = open("resize.bmp","rb") #b is for binary
    contents = bytearray(infile.read())
    infile.close()

    # please refer to bitmap file description (link below) to understand the following code
    #http://www.dragonwins.com/domains/getteched/bmp/bmpfileformat.htm
    #Get the size of this image
    data = [contents[2], contents[3], contents[4], contents[5]]
    fileSize = struct.unpack("I", bytearray(data))
    print "Size of file:", fileSize[0]

    #Get the header offset amount
    data = [contents[10], contents[11], contents[12], contents[13]]
    offset = struct.unpack("I", bytearray(data))
    print "Offset:", offset[0]

    #Get the number of colors used
    data = [contents[46], contents[47], contents[48], contents[49]]
    colorsUsed = struct.unpack("I", bytearray(data))
    print "Number of colors used:", colorsUsed[0]

    #Create color definition array and init the array of color values
    colorIndex = bytearray(colorsUsed[0])
    for i in range(colorsUsed[0]):
        colorIndex.append(0)

    #Assign the colors to the array
    startOfDefinitions = 54
    for i in range(colorsUsed[0]):    
        colorIndex[i] = contents[startOfDefinitions + (i * 4)]

    #Make a string to hold the output of our script
    arraySize = (len(contents) - offset[0]) / 2
    # outputString = "#ifndef BEER_H" + '\r'
    # outputString += "#define BEER_H" + '\r\r'
    outputString = "DRAM_ATTR const uint8_t "
    outputString += outarray + "[" + str(arraySize) + "] = {" + '\r'

    #Start coverting spots to values
    #Start at the offset and go to the end of the file
    for i in range(offset[0], fileSize[0], 2):
        colorCode1 = contents[i]
        actualColor1 = colorIndex[colorCode1] #Look up this code in the table

        colorCode2 = contents[i + 1]
        actualColor2 = colorIndex[colorCode2] #Look up this code in the table

        #Take two bytes, squeeze them to 4 bits
        #Then combine them into one byte
        compressedByte = (actualColor1 >> 4) | (actualColor2 & 0xF0)

        #Add this value to the string
        outputString += hex(compressedByte) + ", "

        #Break the array into a new line every 16 entries
        if i % 32 == 0:
            outputString += '\r'
        
    #Once we've reached the end of our input string, pull the last two
    #characters off (the last comma and space) since we don't need
    #them. Top it off with a closing bracket and a semicolon.
    outputString = outputString[:-2]
    outputString += "};"
    # outputString += "};" + '\r\r'
    # outputString += "#endif"
    #Write the output string to our output file
    outfile = open("output.txt","w")
    outfile.write(outputString)
    outfile.close()

    print "output.txt complete"
    print "Copy and paste this array into a image.h or other header file"

if __name__ == "__main__":
    main(sys.argv[1:])
