import os, requests, glob
from dotenv import load_dotenv
from doc_parser.vision_ai import getVisionAiJSON
from doc_parser.converter import pdfToPng
from doc_parser.pdf_to_text import pdfToText
from doc_parser.prepare_vision_ai_json import modifyJSON
from doc_parser.for_linkedin.crop_image import cropImg
from doc_parser.for_linkedin.vision_json_to_general_json import createGeneralJSON
from doc_parser.for_linkedin.fill_skills_for_ai import fillSkills
from doc_parser.combine_cv_images import combineImages

def main(tmp_dir):
  load_dotenv()
  if "ID" in os.environ and "TOKEN" in os.environ:
    token = os.getenv("TOKEN")
    cvID = os.getenv("ID")
    url = "https://our-rock-313313.ew.r.appspot.com/api/Cvs/" + cvID
    urlForFile = "https://our-rock-313313.ew.r.appspot.com/api/Cvs/" + cvID + "/file"
    headers = {"Authorization": "Bearer {}".format(token)}
  cvsPath = glob.glob(tmp_dir + "/*.pdf")  # Gaunam visų CV path'us

  for cvIndex in range(len(cvsPath)):
    cvFileName = os.path.basename(cvsPath[cvIndex])
    imgPathList = pdfToPng(tmp_dir, cvsPath[cvIndex])  # gauname PNG CV path list'a
    # crop'inam linkedIn CV (grazina img path list)
    cropedImgPathList = cropImg(tmp_dir, imgPathList)
    combinedImgPathList = combineImages(tmp_dir, cropedImgPathList)
    combinedJsonPath = getVisionAiJSON(combinedImgPathList)
    modifiedCombinedJsonPath = modifyJSON(combinedImgPathList)
    processInfo, multiplePositionsInfo = createGeneralJSON(tmp_dir, modifiedCombinedJsonPath, cvFileName)
    print(processInfo)
    fillSkills(tmp_dir, cvIndex, multiplePositionsInfo)
    #fillSkills(tmp_dir, cvFileName, cvIndex, multiplePositionsInfo)
    deleteFiles(imgPathList)
    deleteFiles(cropedImgPathList)
    deleteFiles(combinedImgPathList)
    deleteFiles(combinedJsonPath)
    deleteFiles(modifiedCombinedJsonPath)

def getCvLabels(url, headers):
  response = requests.get(url, headers=headers)

  if response.status_code != 401:
    print(response.json())
  else:
    print("Reikia atnaujinti TOKEN")

def getCvFile(url, headers):
  response = requests.get(url, headers=headers)
  if response.status_code != 401:
    print(response)
    with open(tmp_dir + "/temp.pdf", "wb") as fd:
      for chunk in response.iter_content(2000):
        fd.write(chunk)
  else:
    print("Reikia atnaujinti TOKEN")

def postCvFile(url, headers, filePath):
  myfile = {"file": open(filePath[0], "rb")}
  response = requests.post(url, files=myfile, headers=headers)
  print(response)

def updateCvLabels(url, headers):
  # patch method
  data = {"description": {"op": "Replace", "value": "Updated value here"}}
  patchResponse = requests.patch(url, json=data, headers=headers)
  print(patchResponse.status_code)

def deleteFiles(filesPath):
  for file in filesPath:
    os.remove(file)

if __name__ == "__main__":
  main()

