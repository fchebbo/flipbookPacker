'''
08/2018
Flipbook Packer

Written by Seth Hall
seth@pixill.com
https://www.pixill.com

Set the execution variables.
Uncomment the def you want to use then execute the script.

Stagger Packing and Super Packing both expect a total image
sequence on disk of 64 frames. This will give you a final
image of 8x8 rows and columns.

Super Packing if using 192 or 256 total frames:
	* Alpha channel is packed if you are using 256
	Frame[1-64].R
	Frame[65-128].G
	Frame[129-192].B
	Frame[193-256].A

Stagger Packing if using 192 or 256 frames:
	* Alpha channel is packed if you are using 256
	Frame[1-4] = Image001.RGBA
	Frame[5-8] = Image002.RGBA
	Frame[9-12] = Image003.RGBA
	Frame[13-16] = Image004.RGBA
'''

import math
import os
import tkinter as tk
from tkinter import filedialog

import PIL
from PIL import Image

#
# execution variables start

seqPath = 'C:/img/' 	# path to your image sequence on disk.
imgFormat = 'tif'		# image format to look for on disk from the seqPath variable.
pilFormat = 'tiff'		# image format to save out as. if tif format, you need 2 f's (ex, 'tiff').
compress = 'tiff_lzw'	# tif compression if using tif format.
atlasRow = 6 			# total texture atlas columns. only used for atlasLayout().
atlasCol = 6			# total texture atlas rows. only used for atlasLayout().
numFiles = 0
if pilFormat == 'tiff':
	saveFormat = 'tif'
else:
	saveFormat = pilFormat

# execution variables end
#

##-- UI defs START --
def getFolder():
	folderChosen = filedialog.askdirectory()

	print ("FOLDER CHOSEN IS: " + folderChosen)
	if folderChosen:
		if not folderChosen[-1]=='/':
			folderChosen = folderChosen +'/'
		folderNameVariable.set(folderChosen)
		path, dirs, files = next(os.walk(folderChosen))
		global numFiles
		numFiles = len(files)
		fileCountLabel.config(text="This folder has: " +  str(numFiles) + " files")
		print (algorithmVariable.get())
		print (numRowsVariable.get())

def doPack():
	algo = algorithmVariable.get()
	imgPath = folderNameVariable.get()
	if not os.path.exists(imgPath):
		statusVariable.set("SELECT A FOLDER!!!")
		return
	global imgFormat
	imgFormat = 'tif'
	global pilFormat 
	pilFormat = pilFormatVariable.get()
	
	outputFile = ""
	if algo == "atlasLayout" :
		rows = int(numRowsVariable.get())
		cols = int(numColsVariable.get())
		#if we're doing atlasPack and rows or variables isnt set, make it a square
		if (rows == 0 or cols == 0):
			print (numFiles)
			ans = 0
			while ans*ans < numFiles:
				ans += 1
			rows = ans
			numRowsVariable.set(ans)
			cols = ans
			numColsVariable.set(ans)
		outputFile = atlasLayout(rows, cols, imgPath)
	elif algo == "staggerPack":
		outputFile = staggerPack(imgPath)
	else:
		outputFile = superPack(imgPath)
	print ("ALGORITHM IS: " + algorithmVariable.get())
	print ("NUM ROWS IS: " + numRowsVariable.get())
	print ("NUM COLS IS: " + numColsVariable.get())
	print ("FOLDERNAME IS " + folderNameVariable.get())

	if not outputFile is None:
		statusVariable.set("Pack successful:")
		outputPathVariable.set(outputFile)
	else:
		outputPathVariable.set("NONE")

def openOutput():
	if outputPathVariable.get()[0] =='<':
		statusVariable.set("Please Pack first")
	else:
		os.startfile(outputPathVariable.get())
## UI defs END

def compareDimension(image, imPath, width, height):
	img = Image.open(imPath + image)
	w, h = img.size

	if w == width and h == height:
		return True
	elif w != width or h != height:
		return False

def getImages(images, imPath, width, height):
	catch = []
	for file in images:
		if file.endswith(imgFormat):
			check = compareDimension(file, imPath, width, height)

			if check == True:
				catch.append(file)

	return catch

def atlasLayout(row, col, imPath):
	images = os.listdir(imPath)

	if len(images) < 1:
		print('No images in folder to Atlas Layout')
		statusVariable.set('No images in folder to Atlas Layout')
	else:
		name = images[0].split('.')
		exportPath = imPath + '_texture/'
		atlasTex = exportPath + 'atlas_' + name[0] + '.' + saveFormat

		if os.path.exists(exportPath) == False:
			os.makedirs(exportPath)

		# load the first image then determine the width and height
		img = Image.open(imPath + images[0], 'r')
		w, h = img.size
		hasAlpha = img.mode == 'RGBX'
		dimensions = [w * row, h * col]

		if hasAlpha == True:
			newImg = Image.new('RGBX', dimensions)
		elif hasAlpha == False:
			newImg = Image.new('RGB', dimensions)

		# lets loop through the images to make sure we're only getting the format we want
		# and to check and ensure the images are all the same width and height
		imagesToProcess = getImages(images, imPath, w, h)

		for i in range(len(imagesToProcess)):
			currCol = i % row
			currRow = math.floor(i / row)
			leftPixel = currCol * w
			topPixel = currRow * h

			currentImg = Image.open(imPath + imagesToProcess[i])

			if hasAlpha == True:
				newImg.paste(currentImg, (leftPixel, topPixel))

				r, g, b, a = currentImg.split()
				
				newAlphaImg = Image.merge('RGBX', (r, g, b, a))
			elif hasAlpha == False:
				newImg.paste(currentImg, (leftPixel, topPixel))

		if pilFormat == 'tiff':
			newImg.save(atlasTex, pilFormat, compression=compress)
		else:
			newImg.save(atlasTex, pilFormat)

		print(atlasTex)
		return atlasTex

def staggerPack(imPath):
	images = os.listdir(imPath)

	if len(images) < 1:
		print('No images in folder to Stagger Pack')
		statusVariable.set('No images in folder to Stagger Pack')
	else:
		name = images[0].split('.')
		exportPath = imPath + '_texture/'
		atlasTex = imPath + '_texture/staggerPack_' + name[0] + '.' + saveFormat

		img = Image.open(imPath + images[0])
		w, h = img.size

		imagesToProcess = getImages(images, imPath, w, h)

		if len(imagesToProcess) != 192 and len(imagesToProcess) != 256:
			print('Stagger Packing requires sequences of 192 for RGB or 256 for RGBA packing.')
			statusVariable.set('Stagger Packing requires sequences of 192 for RGB or 256 for RGBA packing.')
		else:
			if os.path.exists(exportPath) == False:
				os.makedirs(exportPath)

			channelsToPack = 3
			channels = 'RGB'

			if len(imagesToProcess) == 256:
				channels = 'RGBX'
				channelsToPack = 4

			atlasFrames = int(len(imagesToProcess) / channelsToPack)
			square = int(math.sqrt(atlasFrames))

			dimensions = [w * square, h * square]

			newImg = Image.new(channels, dimensions)
			tempAlphaImg = Image.new(channels, dimensions)

			if channelsToPack == 4:
				r, g, b, a = newImg.split()
			elif channelsToPack == 3:
				r, g, b = newImg.split()

			if channelsToPack == 4:
				newAlphaImg = Image.new(channels, dimensions)

			# loop through all of our images, re: 192 or 256
			for i in range(len(imagesToProcess)):
				row = math.floor(i / (square * channelsToPack))

				if i % channelsToPack == 0:
					column = int((i / channelsToPack) % square)

					leftPixel = column * w
					topPixel = row * h

					for x in range(channelsToPack):
						if x % channelsToPack == 0:
							redImg = Image.open(imPath + imagesToProcess[i], mode='r')
							newImg.paste(redImg, (leftPixel, topPixel))

							if channelsToPack == 4:
								rr, rg, rb, ra = newImg.split()
							elif channelsToPack == 3:
								rr, rg, rb = newImg.split()

						if x % channelsToPack == 1:
							blueImg = Image.open(imPath + imagesToProcess[i+1], mode='r')
							newImg.paste(blueImg, (leftPixel, topPixel))

							if channelsToPack == 4:
								gr, gg, gb, ga = newImg.split()
							elif channelsToPack == 3:
								gr, gg, gb = newImg.split()

						if x % channelsToPack == 2:
							greenImg = Image.open(imPath + imagesToProcess[i+2], mode='r')
							newImg.paste(greenImg, (leftPixel, topPixel))

							if channelsToPack == 4:
								br, bg, bb, ba = newImg.split()
							elif channelsToPack == 3:
								br, bg, bb = newImg.split()

						if x % channelsToPack == 3:
							alphaImg = Image.open(imPath + imagesToProcess[i+3], mode='r')
							tempAlphaImg.paste(alphaImg, (leftPixel, topPixel))

							ar, ag, ab, aa = tempAlphaImg.split()

					if channelsToPack == 4:
						newImg = Image.merge(channels, (rr, gg, bb, ar))
					elif channelsToPack == 3:
						newImg = Image.merge(channels, (rr, gg, bb))

			if pilFormat == 'tiff':
				newImg.save(atlasTex, pilFormat, compression=compress)
			else:
				newImg.save(atlasTex, pilFormat)

			print(atlasTex)
			return atlasTex

def superPack(imPath):
	images = os.listdir(imPath)

	if len(images) < 1:
		print('No images in folder to Super Pack')
	else:
		name = images[0].split('.')
		exportPath = imPath + '_texture/'
		atlasTex = imPath + '_texture/superPack_' + name[0] + '.' + saveFormat

		img = Image.open(imPath + images[0])
		w, h = img.size

		imagesToProcess = getImages(images, imPath, w, h)

		if len(imagesToProcess) != 192 and len(imagesToProcess) != 256:
			print('Super Packing requires sequences of 192 for RGB or 256 for RGBA packing.')
			statusVariable.set('Super Packing requires sequences of 192 for RGB or 256 for RGBA packing.')
		else:
			if os.path.exists(exportPath) == False:
				os.makedirs(exportPath)

			channelsToPack = 3
			channels = 'RGB'

			if len(imagesToProcess) == 256:
				channels = 'RGBX'
				channelsToPack = 4

			atlasFrames = int(len(imagesToProcess) / channelsToPack)
			square = int(math.sqrt(atlasFrames))

			dimensions = [w * square, h * square]

			if channelsToPack == 4:
				newImg = Image.new(channels, dimensions)
				r, g, b, a = newImg.split()
			elif channelsToPack == 3:
				newImg = Image.new(channels, dimensions)
				r, g, b = newImg.split()

			if channelsToPack == 4:
				tempAlphaImg = Image.new(channels, dimensions)

			# loop through all of our images, re: 192 or 256
			imgCount = int(0)
			for i in range(channelsToPack):
				for x in range(atlasFrames):
					col = x % square
					row = math.floor(x / square)

					leftPixel = col * w
					topPixel = row * h

					if i % channelsToPack == 0:
						redImg = Image.open(imPath + imagesToProcess[imgCount], mode='r')
						newImg.paste(redImg, (leftPixel, topPixel))

						if channelsToPack == 4:
							rr, rg, rb, ra = newImg.split()
						elif channelsToPack == 3:
							rr, rg, rb = newImg.split()

					elif i % channelsToPack == 1:
						blueImg = Image.open(imPath + imagesToProcess[imgCount], mode='r')
						newImg.paste(blueImg, (leftPixel, topPixel))

						if channelsToPack == 4:
							gr, gg, gb, ga = newImg.split()
						elif channelsToPack == 3:
							gr, gg, gb = newImg.split()

					elif i % channelsToPack == 2:
						greenImg = Image.open(imPath + imagesToProcess[imgCount], mode='r')
						newImg.paste(greenImg, (leftPixel, topPixel))

						if channelsToPack == 4:
							br, bg, bb, ba = newImg.split()
						elif channelsToPack == 3:
							br, bg, bb = newImg.split()

					if channelsToPack == 4:
						if i % channelsToPack == 3:
							alphaImg = Image.open(imPath + imagesToProcess[imgCount], mode='r')
							tempAlphaImg.paste(alphaImg, (leftPixel, topPixel))

							ar, ag, ab, aa = tempAlphaImg.split()

					imgCount = imgCount + 1

			if channelsToPack == 4:
				newImg = Image.merge('RGBX', (rr, gg, bb, ar))
			elif channelsToPack == 3:
				newImg = Image.merge('RGB', (rr, gg, bb))
			
			if pilFormat == 'tiff':
				newImg.save(atlasTex, pilFormat, compression=compress)
			else:
				newImg.save(atlasTex, pilFormat)

			print(atlasTex)
			return atlasTex
# START UI STUFF

root = tk.Tk()
algorithmList = ["atlasLayout", "staggerPack", "superPack"]

root.title("Flipbook Packer")
root.geometry("600x600")

# Select Folder Button
selectFolderButton = tk.Button(root, text="Select Folder", fg="white", bg = "#263D42", command=getFolder)
selectFolderButton.grid(row=0,column=1)

# The selected folder
folderNameVariable = tk.StringVar(root)
folderLabel = tk.Label(root,textvariable=folderNameVariable, bg="#A1FFE3")
folderLabel.grid(row=0,column=0)
folderLabel.config(text="No Folder Currently Selected")

# Number of files in this folder
fileCountLabel = tk.Label(root, bg="#FFEE6F")
fileCountLabel.grid(row=0,column=2)
fileCountLabel.config(text="")

# Packing Algorithm Label
algorithmLabel = tk.Label(root, text="Packing Algorithm", bg="#A1FFE3")
algorithmLabel.grid(row=1,column=0)

# Packing Algorithm dropdown 
algorithmVariable = tk.StringVar(root)
algorithmVariable.set(algorithmList[0])
algorithmOpt = tk.OptionMenu(root,algorithmVariable, *algorithmList)
algorithmOpt.grid(row=1,column=1)

# Num Rows Label
numRowsLabel = tk.Label(root,text="Num Rows (if using atlasPack): ", bg="#A1FFE3")
numRowsLabel.grid(row=2,column=0)

# Num Rows Entry
numRowsVariable = tk.StringVar(root, value='0')
numRowsEntry = tk.Entry(root,textvariable=numRowsVariable,justify= 'right')
numRowsEntry.grid(row=2, column=1)

# Num Cols Label
numColsLabel = tk.Label(root,text="Num Cols (if using atlasPack): ", bg="#A1FFE3")
numColsLabel.grid(row=3,column=0)

# Num Cols Entry
numColsVariable = tk.StringVar(root, value='0')
numColsEntry = tk.Entry(root,textvariable=numColsVariable,justify= 'right')
numColsEntry.grid(row=3, column=1)

# Img Format Label
imgFormatLabel = tk.Label(root,text="Image Foramt (Input): ", bg="#A1FFE3")
imgFormatLabel.grid(row=4,column=0)

# Img Format Entry
imgFormatVariable = tk.StringVar(root, value='tif')
imgFormatEntry = tk.Entry(root, textvariable=imgFormatVariable)
imgFormatEntry.grid(row=4, column=1)

# Img Format Label
pilFormatLabel = tk.Label(root,text="Image Foramt (Output): ", bg="#A1FFE3")
pilFormatLabel.grid(row=5,column=0)

# Img Format Entry
pilFormatVariable = tk.StringVar(root, value='tiff')
pilFormatEntry = tk.Entry(root, textvariable=pilFormatVariable)
pilFormatEntry.grid(row=5, column=1)

# Status  Label
statusVariable = tk.StringVar(root)
StatusLabel = tk.Label(root,textvariable=statusVariable, bg="#c242f5")
StatusLabel.grid(row=6,column=0)

#Output Path
outputPathVariable = tk.StringVar(root, value='<OUTPUT GOES HERE>')
outputPathEntry= tk.Entry(root, state="readonly", textvariable=outputPathVariable)
outputPathEntry.grid(row=6, column=1)

#Open Output
openOutputButton = tk.StringVar(root, value='...')
openOutputButton = tk.Button(text="...", fg="white", bg = "#263D42", command=openOutput)
openOutputButton.grid(row=6, column=2)

#Pack button
packButton = tk.Button(root, text="PACK", fg="white", bg = "#263D42", command=doPack)
packButton.grid(row=7,column=1)

root.mainloop()

#
# Uncomment out the packing function you wish to use

#atlasLayout(atlasRow, atlasCol, seqPath)

#staggerPack(seqPath)

#superPack(seqPath)
