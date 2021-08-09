import numpy as np
from PIL import Image

def combination(tmp_dir, imgs, name):
  images = [Image.open(i) for i in imgs]
  imagesCombination = np.vstack(images)
  imagesCombination = Image.fromarray(imagesCombination)
  imagesCombination.save(tmp_dir + '/' + name + '.png')

def combineImages(tmp_dir, imgList):
  # Sujungiam visų psl nuotraukas į vieną nuotrauką (atskirai kairę ir dešinę pusę)
  middleIndex = len(imgList) // 2
  leftImages = imgList[:middleIndex]
  rightImages = imgList[middleIndex:]
  combination(tmp_dir, leftImages, "left")
  combination(tmp_dir, rightImages, "right")
  return [tmp_dir + '/left.png', tmp_dir + '/right.png']

