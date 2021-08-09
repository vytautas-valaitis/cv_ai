import pdfplumber

def pdfToText(path, tmp_dir):
  with pdfplumber.open(path) as pdf:
    allText = ""
    for pdfPage in pdf.pages:
      singlePageText = pdfPage.extract_text()
      allText = allText + "\n" + singlePageText

  text_file = open(tmp_dir + "/textFromPdf.txt", "wt", encoding="utf-8")
  text_file.write(allText)
  text_file.close()

  return [path]  # grazinam kaip list, jog visur butu vienodas path formatas

