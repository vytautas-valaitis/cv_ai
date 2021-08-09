import json
import os


def modifyJSON(path):

    resultPath = []

    for filePath in path:
        with open(os.path.splitext(filePath)[0] + ".json", "r") as dataFile:
            data = json.load(dataFile)

        newJSON = {}
        newJSON["pages"] = []

        for pageNum in range(len(data)):  # einam per visus psl
            newJSON["pages"].insert(pageNum, {})
            newJSON["pages"][pageNum]["blocks"] = []
            if "fullTextAnnotation" in data[pageNum]:
                newJSON["pages"][pageNum]["allPageText"] = data[pageNum]["fullTextAnnotation"]["text"]
                # ištrinam JSON dalį, kur info saugojama tik po vieną žodį
                del data[pageNum]["textAnnotations"]
                prefix = data[pageNum]["fullTextAnnotation"]["pages"]
                prefixNEW = newJSON["pages"][pageNum]["blocks"]
                for page in range(len(prefix)):
                    for block in range(len(prefix[page]["blocks"])):
                        prefixNEW.append({})
                        prefixNEW[block]["positions"] = []
                        prefixNEW[block]["paragraphs"] = []
                        prefixNEW[block]["text"] = ""
                        for positions in prefix[page]["blocks"][block]["boundingBox"]["vertices"]:
                            prefixNEW[block]["positions"].append({"x": positions["x"], "y": positions["y"]})
                        for paragraph in range(len(prefix[page]["blocks"][block]["paragraphs"])):
                            prefix2 = prefix[page]["blocks"][block]["paragraphs"][paragraph]
                            prefixNEW2 = prefixNEW[block]["paragraphs"]
                            prefixNEW2.append({})
                            prefixNEW2[paragraph]["positions"] = []
                            prefixNEW2[paragraph]["words"] = []
                            prefixNEW2[paragraph]["text"] = ""
                            for positions in prefix2["boundingBox"]["vertices"]:
                                prefixNEW2[paragraph]["positions"].append({"x": positions["x"], "y": positions["y"]})
                            for word in range(len(prefix2["words"])):
                                prefixNEW2[paragraph]["words"].append({})
                                prefixNEW2[paragraph]["words"][word]["positions"] = []
                                prefixNEW2[paragraph]["words"][word]["symbols"] = []
                                prefixNEW2[paragraph]["words"][word]["text"] = ""
                                for positions in prefix2["words"][word]["boundingBox"]["vertices"]:
                                    prefixNEW2[paragraph]["words"][word]["positions"].append(
                                        {
                                            "x": positions["x"],
                                            "y": positions["y"],
                                        }
                                    )
                                for symbol in range(len(prefix2["words"][word]["symbols"])):
                                    prefixNEW2[paragraph]["words"][word]["symbols"].append({})
                                    prefixNEW2[paragraph]["words"][word]["symbols"][symbol]["positions"] = []
                                    prefixNEW2[paragraph]["words"][word]["symbols"][symbol]["text"] = prefix2["words"][word][
                                        "symbols"
                                    ][symbol]["text"]
                                    prefixNEW2[paragraph]["words"][word]["text"] += prefix2["words"][word]["symbols"][
                                        symbol
                                    ]["text"]
                                    for positions in prefix2["words"][word]["symbols"][symbol]["boundingBox"]["vertices"]:
                                        prefixNEW2[paragraph]["words"][word]["symbols"][symbol]["positions"].append(
                                            {
                                                "x": positions["x"],
                                                "y": positions["y"],
                                            }
                                        )
                                prefixNEW2[paragraph]["text"] += prefixNEW2[paragraph]["words"][word]["text"] + " "
                            prefixNEW2[paragraph]["text"] = prefixNEW2[paragraph]["text"].rstrip()
                            prefixNEW[block]["text"] += prefixNEW2[paragraph]["text"] + " "
                        prefixNEW[block]["text"] = prefixNEW[block]["text"].rstrip()

        with open(os.path.splitext(filePath)[0] + "Modified.json", "w") as dataFile:
            data = json.dump(newJSON, dataFile)
        resultPath.append(os.path.splitext(filePath)[0] + "Modified.json")

    return resultPath
