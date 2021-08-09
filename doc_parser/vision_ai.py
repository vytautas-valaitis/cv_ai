# export GOOGLE_APPLICATION_CREDENTIALS="visionAPI.json"
from google.protobuf.json_format import MessageToJson
from google.cloud import vision
import io, os, json

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vision_api.json"  # visible in this process + all children

def getVisionAiJSON(documentPath):
  # Read text from image and extract info about it
  resultPath = []
  client = vision.ImageAnnotatorClient()
  for fileName in documentPath:
    data = []
    with io.open(fileName, "rb") as imageFile:
      content = imageFile.read()
      image = vision.Image(content=content)
      # Performs label detection on the image file
      response = client.document_text_detection(image=image)
      data.append(json.loads(MessageToJson(response._pb)))

    resultPath.append(os.path.splitext(fileName)[0] + ".json")
    with open(resultPath[-1], "w") as f:
      json.dump(data, f)

  return resultPath

