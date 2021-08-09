from pdf2image import convert_from_bytes

def pdfToPng(tmp_dir, path):
  print(path)
  with open(path, "rb") as pdf:
    images = convert_from_bytes(pdf.read())
  imgList = []
  for i in range(len(images)):
    images[i].save(tmp_dir + "/page" + str(i) + ".png", "PNG")
    imgList.append(tmp_dir + "/page" + str(i) + ".png")
  return imgList

