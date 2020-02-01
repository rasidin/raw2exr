import sys
import os
import csv
import array

import numpy
import rawpy
import OpenEXR

def printLog():
	print 'NEF to EXR'
	print 'NEF raw images to linear color space exr'
	print 'author minseob'

def printUsage():
	print 'Usage : nef2exr <filelist> <outputfilename>'

def getInputFileInfo(csvfilepath):
	output = []
	if (os.path.exists(csvfilepath)):
		with open(csvfilepath) as csvfile:
			csvline = csv.reader(csvfile)
			for row in csvline:
				output.append(row)
	return output

def main():
	printLog()
	
	argv = sys.argv
	argc = len(argv)

	if (argc < 3):
		printUsage()
		return -1
	
	csvfilepath = argv[1]
	outputfilepath = argv[2]
	
	filelist = getInputFileInfo(csvfilepath)
	if (len(filelist) == 0):
		return -1

	imgwidth = 0
	imgheight = 0
	rootdir = os.path.dirname(csvfilepath)
	rawdatalist = []
	mergedRed = []
	mergedGreen = []
	mergedBlue = []
	for filedata in filelist:
		filefullpath = filedata[0]
		if (os.path.isabs(filedata[0]) is False):
			filefullpath = os.path.join(rootdir, filedata[0])
	
		ev = float(filedata[1])
		exposure = pow(2, ev)
		if os.path.exists(filefullpath):
			print 'Open file : ' + filefullpath
			print 'EV : %f -> %f'%(ev, exposure)
		
			print 'Loading...'
			rawdata = rawpy.imread(filefullpath)
			print 'Converting...'
			raw2rgb = rawdata.postprocess(gamma=(1,1), no_auto_bright=True, output_bps=16)
			imgwidth = rawdata.sizes.raw_width
			imgheight = rawdata.sizes.raw_height
			
			if len(mergedRed) == 0:
				mergedRed = numpy.resize([], imgwidth * imgheight)
			if len(mergedGreen) == 0:
				mergedGreen = numpy.resize([], imgwidth * imgheight)
			if len(mergedBlue) == 0:
				mergedBlue = numpy.resize([], imgwidth * imgheight)
			
			progress = 0
			sys.stdout.write('[')
			for y in range(imgheight):
				curprog = y * 30 / imgheight
				if progress != curprog:
					progress = curprog
					sys.stdout.write('-')
				for x in range(imgwidth):
					index = x + y * imgwidth
					r = raw2rgb[y][x][0]
					g = raw2rgb[y][x][1]
					b = raw2rgb[y][x][2]
					fr = float(r) / 32767.0 * exposure
					fg = float(g) / 32767.0 * exposure
					fb = float(b) / 32767.0 * exposure
					if r > 10 and r < 32500:
						mergedRed[index] = fr
					if g > 10 and g < 32500:
						mergedGreen[index] = fg
					if b > 10 and b < 32500:
						mergedBlue[index] = fb
			print ']'
			
	outputEXR = OpenEXR.OutputFile(outputfilepath, OpenEXR.Header(imgwidth, imgheight))
	
	dataRed = array.array('f', mergedRed).tostring()
	dataGreen = array.array('f', mergedGreen).tostring()
	dataBlue = array.array('f', mergedBlue).tostring()
	outputEXR.writePixels({'R': dataRed, 'G': dataGreen, 'B': dataBlue})
	
	outputEXR.close()

if __name__ == '__main__':
	main()
