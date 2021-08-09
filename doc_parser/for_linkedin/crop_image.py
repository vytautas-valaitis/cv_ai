from PIL import Image

def cropImg(tmp_dir, imgList):
  cropedImgList = []

  newImgAreaRight = (560, 0, 1700, 2200)  # left, top, right, bottom
  # Skaičiai parinkti konkrečiai linkedin CV. Tikslas - atsirti mėlyną kairę CV pusę
  newImgAreaLeft = (0, 0, 560, 2200)

  num = 0
  for image in imgList:
    img = Image.open(image)
    newImgLeft = img.crop(newImgAreaLeft)
    newImgLeft.save(tmp_dir + "/cropedLeft" + str(num) + ".png", "PNG")
    newImgRight = img.crop(newImgAreaRight)
    newImgRight.save(tmp_dir + "/cropedRight" + str(num) + ".png", "PNG")
    cropedImgList.append(tmp_dir + "/cropedLeft" + str(num) + ".png")
    num += 1

  for imageNumber in range(len(imgList)):
    cropedImgList.append(tmp_dir + "/cropedRight" + str(imageNumber) + ".png")

  return cropedImgList

