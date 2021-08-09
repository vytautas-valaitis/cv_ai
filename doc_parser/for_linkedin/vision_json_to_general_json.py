import os, re, json, calendar
import doc_parser.constant as constant

generalJSON = {}
deviationY = 10  # leidžiama paklaida imant vienos eilutės tekstą
multiplePositionsInfo = []  # Saugom info apie darbus, jog būtų galima panaudoti traukiant skills'us


def analyseRightCvPart(path):
  with open(os.path.splitext(path)[0] + ".json", "r") as dataFile:
    data = json.load(dataFile)
  getPersonName(data)
  for block in range(len(data["pages"][0]["blocks"])):
    matchEducation = constant.PATTERN_EDUCATION.search(data["pages"][0]["blocks"][block]["text"])
    matchExperience = constant.PATTERN_EXPERIENCE.search(data["pages"][0]["blocks"][block]["text"])
    if matchEducation is not None:
      experienceEndBlock = block
      educationStartBlock = block + 1
      educationEndBlock = len(data["pages"][0]["blocks"])
    if matchExperience is not None:
      experienceStartBlock = block + 1
  if "experienceEndBlock" not in locals():
    # Suveiks, jei CV nebus education dalies
    experienceEndBlock = len(data["pages"][0]["blocks"])
  if "experienceStartBlock" in locals():
    allExperienceWords = getAllWordsFromBlocks(experienceStartBlock, experienceEndBlock, data)
    analyseExperienceWords(allExperienceWords)
  if "educationStartBlock" in locals():
    allEducationWords = getAllWordsFromBlocks(educationStartBlock, educationEndBlock, data)
    analyseEducationWords(allEducationWords)


def getPersonName(data):
  allWords = getAllWordsFromBlocks(0, 1, data)
  linePosition = allWords[0]["positions"][0]["y"]

  index = 0
  while index < len(allWords):
    currentWord = allWords[index]["text"]
    yPos = allWords[index]["positions"][0]["y"]
    if linePosition + deviationY > yPos and linePosition - deviationY < yPos:
      generalJSON["Name"] += currentWord + " "
    else:
      generalJSON["Name"] = generalJSON["Name"].rstrip()
      break
    index += 1


def getAllWordsFromBlocks(startBlock, endBlock, data):
  allWords = []
  for blockInfo in data["pages"][0]["blocks"][startBlock:endBlock]:
    for paragraph in range(len(blockInfo["paragraphs"])):
      index = 0
      while index < len(blockInfo["paragraphs"][paragraph]["words"]):
        # susirašom visus žodžius į masyvą, kad būtų lengviau atlikti visus tikrinimus
        wordInfo = blockInfo["paragraphs"][paragraph]["words"][index]
        matchPage = constant.PATTERN_PAGE.search(wordInfo["text"])
        if matchPage is not None:
          # Jei surandame Page x of x, praleidžiam
          index += 3
        else:
          allWords.append(blockInfo["paragraphs"][paragraph]["words"][index])
        index += 1

  return allWords


def analyseEducationWords(allWords):
  educationCount = courseCount = 0
  lineIndex = 0
  linePosition = allWords[0]["positions"][0]["y"]
  lineText = [""]
  isEndOfDegree = False
  startYear = endYear = ""
  averageWordsHeight, wordsInLineCount = [0], [0]  # Saugome kiekvienos eilutės žodžių aukščių vidurkį ir žodžių kiekį
  lineLastWordXposition = [0]  # Saugom kiekvienos eilutės paskutinio žodžio pabaigos x poziciją
  index = 0
  while index < len(allWords):
    currentWord = allWords[index]["text"]
    currentWordPositions = allWords[index]["positions"]
    yPos = currentWordPositions[0]["y"]
    if linePosition + deviationY > yPos and linePosition - deviationY < yPos:
      # Tekstas toje pačioje eilutėje
      if not isEndOfDegree:
        # Jei jau pasiekėm datą, tos info mums įrašyti nereikia
        lineText[lineIndex] = addTextAndCheckSpaces(lineText[lineIndex], currentWord)
      averageWordsHeight[lineIndex] += currentWordPositions[3]["y"] - currentWordPositions[0]["y"]
      wordsInLineCount[lineIndex] += 1
      if lineIndex >= 1 and index + 2 < len(allWords):
        # Imam du į priekį žodžius tam, jog jei jie tinka nebeįrašytume jų į lineText
        matchMiddleDot = constant.PATTERN_MID_DOT.search(currentWord)
        matchParentheses = constant.PATTERN_PARENTHESES.search(allWords[index + 1]["text"])
        matchYear = constant.PATTERN_YEAR.search(allWords[index + 2]["text"])
        if matchMiddleDot is not None and matchParentheses is not None:
          # Papildomas tikrinimas, jei education dalyje yra nurodomas mėnesis
          isEndOfDegree = True
        if matchYear is not None:
          if matchParentheses is not None:
            # Jei surandam ( ir metus, žinom, kad šitoj eilutėj baigiasi degree
            isEndOfDegree = True
            startYear = allWords[index + 2]["text"]
          else:
            # Įrašom studijų pabaigos metus
            endYear = allWords[index + 2]["text"]
    else:
      linePosition = yPos
      index -= 1
      averageWordsHeight[lineIndex] = averageWordsHeight[lineIndex] / wordsInLineCount[lineIndex]
      lineLastWordXposition[lineIndex] = allWords[index]["positions"][1]["x"]
      if isEndOfDegree:
        lineText = analyseOneDegreeData(averageWordsHeight, lineLastWordXposition, lineText)
        if len(lineText[1]) > 2:
          # Išsaugom tik jei degree sudaro bent 3 simboliai (nes kur mokyklos, ten degree tik taškas)
          degreeType = getDegreeType(startYear, endYear)
          amount = getAmountOfDegrees(educationCount, courseCount, degreeType)
          lineText = removeSpacesAndSymbols(lineText)
          addEducationOrCourseRecord(amount, lineText, degreeType, startYear, endYear)
          educationCount, courseCount = increaseAmountOfDegrees(educationCount, courseCount, degreeType)
        averageWordsHeight, wordsInLineCount, lineLastWordXposition = [0], [0], [0]
        lineIndex = 0
        lineText = [""]
        startYear, endYear = "", ""
        isEndOfDegree = False
      else:
        averageWordsHeight.append(0)
        wordsInLineCount.append(0)
        lineLastWordXposition.append(0)
        lineText.append("")
        lineIndex += 1
    if index + 1 == len(allWords):
      # Pasiekėm paskutinį žodį, tad irgi surašom info
      averageWordsHeight[lineIndex] = averageWordsHeight[lineIndex] / wordsInLineCount[lineIndex]
      lineLastWordXposition[lineIndex] = allWords[index]["positions"][1]["x"]
      lineText = analyseOneDegreeData(averageWordsHeight, lineLastWordXposition, lineText)
      if len(lineText[1]) > 2:
        # Išsaugom tik jei degree sudaro bent 3 simboliai (nes kur mokyklos, ten degree tik taškas)
        degreeType = getDegreeType(startYear, endYear)
        amount = getAmountOfDegrees(educationCount, courseCount, degreeType)
        lineText = removeSpacesAndSymbols(lineText)
        addEducationOrCourseRecord(amount, lineText, degreeType, startYear, endYear)
        educationCount, courseCount = increaseAmountOfDegrees(educationCount, courseCount, degreeType)
    index += 1


def analyseOneDegreeData(averageWordsHeight, lineLastWordXposition, lineText):
  finalText = ["", ""]  # 0 - organizacija, 1 - išsilavinimas(degree)
  finalText[0] = lineText[0]
  # print(averageWordsHeight, lineText, lineLastWordXposition)
  if len(lineText) > 2:
    firstLineHeight = averageWordsHeight[0]
    lastLineHeight = averageWordsHeight[-1]
    for line in range(1, len(lineText) - 1):
      # Tikrinam teksto dydį ir pagal tai nustatom ar tai degree ar organisation
      if abs(averageWordsHeight[line] - firstLineHeight) < abs(averageWordsHeight[line] - lastLineHeight):
        if lineLastWordXposition[0] < lineLastWordXposition[line]:
          # Tikrinam kur baigiasi eilutė. Reikalinga tuo atveju, jei žodžių aukštis "pavestų"
          print("GALIMAI NETEISINGAI IŠSAUGOTA 'EDUCATION' DALIS")
          if lineLastWordXposition[0] < 750:
            # 750 random number, paimtas iš testavimų
            finalText[1] += lineText[line]
          else:
            finalText[0] += lineText[line]
        else:
          finalText[0] += lineText[line]
      else:
        finalText[1] += lineText[line]
        if lineLastWordXposition[line] < lineLastWordXposition[0]:
          print("GALIMAI NETEISINGAI IŠSAUGOTA 'EDUCATION' DALIS")
  finalText[1] += lineText[-1]  # Pridedam pask eilutės tekstą prie išsilavinimo
  return finalText


def getDegreeType(startYear, endYear):
  # Šiuo metu kursus nuo studijų atskiriam tik pagal laiką
  if startYear == endYear:
    return "Courses"
  else:
    return "EducationHistory"


def getAmountOfDegrees(educationCount, courseCount, degreeType):
  if degreeType == "Courses":
    return courseCount
  else:
    return educationCount


def increaseAmountOfDegrees(educationCount, courseCount, degreeType):
  if degreeType == "Courses":
    return educationCount, courseCount + 1
  else:
    return educationCount + 1, courseCount


def removeSpacesAndSymbols(text):
  for line in range(len(text)):
    for symbol in range(len(text[line]) - 1, -1, -1):
      if not text[line][symbol].isalnum():
        # Jei paskutinis simbolis ne skaičius ir ne raidė - pašalinam
        text[line] = text[line][:-1]
      else:
        break
  return text


def addEducationOrCourseRecord(amount, lineText, degreeType, startYear, endYear):
  generalJSON[degreeType].append({})
  generalJSON[degreeType][amount]["OrganisationName"] = lineText[0]
  generalJSON[degreeType][amount]["StartDate"] = startYear
  generalJSON[degreeType][amount]["EndDate"] = endYear
  if degreeType == "Courses":
    generalJSON[degreeType][amount]["Course"] = lineText[1]
  else:
    generalJSON[degreeType][amount]["Degree"] = lineText[1]


def analyseExperienceWords(allWords):
  experienceCount = 0
  lineIndex = 0  # 0 - įmonė, 1 - pareigos, 2 - data
  linePosition = allWords[0]["positions"][0]["y"]
  lineText = ["", "", "", ""]  # įmonė, pareigos, pradž data, pabaigos data
  hasMultiplePositions = False
  checkIfStillMultiplePositions = False
  # Trijų eilučių pozicijos, skirtos tikrinti atstumus ar naujas darbas ar tik pozicija
  linePositions = [None, None, None]
  multiplePositionsCount = 0
  index = 0
  while index < len(allWords):
    yPos = allWords[index]["positions"][0]["y"]
    currentWord = allWords[index]["text"]
    if linePosition + deviationY > yPos and linePosition - deviationY < yPos:
      # Tekstas toje pačioje eilutėje
      linePositions[lineIndex] = yPos  # Saugom visą vienos eilutės tekstą
      if lineIndex == 0 or lineIndex == 1:
        lineText[lineIndex] = addTextAndCheckSpaces(lineText[lineIndex], currentWord)
      if lineIndex == 1 and not hasMultiplePositions:
        matchMonthText = constant.PATTERN_MONTH_TEXT.search(currentWord)
        matchYearText = constant.PATTERN_YEAR_TEXT.search(currentWord)
        if matchMonthText is not None or matchYearText is not None and allWords[index]["positions"][0]["x"] < 400:
          # surandame darbą, kuriame dirbo keliose pozicijose
          hasMultiplePositions = True
          lineText[1] = ""

      if lineIndex == 2 and index + 1 != len(allWords):
        matchParentheses = constant.PATTERN_PARENTHESES.search(currentWord)
        matchNumber = constant.PATTERN_NUMBER.search(allWords[index + 1]["text"])
        matchYear = constant.PATTERN_YEAR.search(currentWord)
        if matchYear is not None:
          # Suradę metus, išsaugom pradžios ir pabaigos (jei yra) datas
          pos = 2
          if lineText[2] != "":
            pos = 3
          lineText[pos] = currentWord

          matchMonth = constant.PATTERN_MONTH.search(allWords[index - 1]["text"])
          if matchMonth is not None:
            # Jei prieš metus tikrai eina mėnuo, konvertuojam mėn į sk ir pridedam prie datos
            lineText[pos] += "-" + str(list(calendar.month_name).index(allWords[index - 1]["text"]))
        if matchParentheses is not None and matchNumber is not None:
          # Jei surandam ( ir skaičių, žinom, kad šitos trys eilutės tinka
          correctLines = True
          if checkIfStillMultiplePositions:
            if linePositions[1] - linePositions[0] > 60:
              lineText[0] = employerName
            else:
              checkIfStillMultiplePositions = False
      if index + 1 == len(allWords) and correctLines:
        # Įrašom experience, jei jis yra pačioje paskutinėje eilutėje
        experienceCount = addEmploymentRecord(experienceCount, lineText)
        if hasMultiplePositions or checkIfStillMultiplePositions:
          multiplePositionsInfo.append(True)
        else:
          multiplePositionsInfo.append(False)
    else:
      linePosition = yPos
      index -= 1
      if lineIndex == 2:
        if correctLines:
          if hasMultiplePositions or checkIfStillMultiplePositions:
            multiplePositionsInfo.append(True)
          else:
            multiplePositionsInfo.append(False)
          experienceCount = addEmploymentRecord(experienceCount, lineText)
          correctLines = False
          if hasMultiplePositions:
            multiplePositionsCount += 1
            lineIndex = 0
          if multiplePositionsCount == 2:
            hasMultiplePositions = False
            checkIfStillMultiplePositions = True
        else:
          # Grįžtam dviem eilutėm aukščiau ir vėl tikrinam iš naujo
          index = firstWordIndex
          linePosition = firstWordPosition
        if hasMultiplePositions:
          lineText = [lineText[0], "", "", ""]
          employerName = lineText[0]
          lineIndex = 0
        else:
          lineText = ["", "", "", ""]
      if lineIndex == 0 or (lineIndex == 1 and hasMultiplePositions):
        firstWordIndex = index
        firstWordPosition = yPos
        correctLines = False
      lineIndex += 1
      if lineIndex == 3:
        lineIndex = 0

    index += 1


def addEmploymentRecord(experienceCount, info):
  generalJSON["EmploymentHistory"].append({})
  generalJSON["EmploymentHistory"][experienceCount]["EmployerName"] = info[0].strip()
  generalJSON["EmploymentHistory"][experienceCount]["JobTitle"] = info[1].strip()
  generalJSON["EmploymentHistory"][experienceCount]["StartDate"] = info[2]
  generalJSON["EmploymentHistory"][experienceCount]["EndDate"] = info[3]
  generalJSON["EmploymentHistory"][experienceCount]["Skills"] = []

  return experienceCount + 1


def analyseLeftCvPart(path):
  with open(os.path.splitext(path)[0] + ".json", "r") as dataFile:
    data = json.load(dataFile)

  for block in range(len(data["pages"][0]["blocks"])):
    matchEmail = constant.PATTERN_EMAIL.search(data["pages"][0]["blocks"][block]["text"])
    matchPhoneNumber = constant.PATTERN_PHONE_NUMBER.search(data["pages"][0]["blocks"][block]["text"])
    matchLanguages = constant.PATTERN_LANGUAGES.search(data["pages"][0]["blocks"][block]["text"])
    matchTopSkills = constant.PATTERN_TOP_SKILS.search(data["pages"][0]["blocks"][block]["text"])
    if matchEmail is not None:
      generalJSON["ContactInformation"] = matchEmail.group(0)
      # Regex pagauna tik vienos eilutės email. Paimam likusį tekstą ir jį prijungiam, jei tai vis dar email
      remainingText = data["pages"][0]["blocks"][block]["text"][matchEmail.end() :]
      remainingWords = remainingText.split()
      for word in remainingWords[0:]:
        matchURL = constant.PATTERN_URL_START.search(word)
        if matchURL is None:
          generalJSON["ContactInformation"] += word

    if matchPhoneNumber is not None:
      generalJSON["Tel.No."] = matchPhoneNumber.group(0).replace(" ", "")
    if matchLanguages is not None:
      prepareWords(block, data, analyseLanguages)
    if matchTopSkills is not None:
      prepareWords(block, data, analyseTopSkills)


def prepareWords(startBlock, data, function):
  allWords = []
  for blockInfo in data["pages"][0]["blocks"][startBlock:]:
    for wordInfo in blockInfo["paragraphs"][0]["words"][0:]:
      # susirašom visus žodžius į masyvą, kad būtų lengviau atlikti visus tikrinimus
      allWords.append(wordInfo)
  function(allWords)


def analyseLanguages(allWords):
  generalJSON["Languages"].append(allWords[1]["text"])  # 0 poz yra "Languages arba Top Skills"
  yPos = allWords[1]["positions"][0]["y"]
  index = 2
  while index < len(allWords):
    if allWords[index]["positions"][0]["y"] - yPos < 70 and allWords[index]["positions"][0]["y"] - yPos > 15:
      # > 15, jog neimtų language type (primary ir pan)
      generalJSON["Languages"].append(allWords[index]["text"])
      yPos = allWords[index]["positions"][0]["y"]
    elif allWords[index]["positions"][0]["y"] - yPos > 15:
      break
    index += 1


def analyseTopSkills(allWords):
  # 0 ir 1 poz yra "Top Skills"
  text = allWords[2]["text"]
  yPos = allWords[2]["positions"][0]["y"]
  index = 3
  while index < len(allWords):
    if allWords[index]["positions"][0]["y"] - yPos < 15:
      text += " " + allWords[index]["text"]
      if index + 1 == len(allWords):
        generalJSON["OtherSkillsFromCV"].append(text)
    elif allWords[index]["positions"][0]["y"] - yPos < 70:
      generalJSON["OtherSkillsFromCV"].append(text)
      text = allWords[index]["text"]
      if index + 1 == len(allWords):
        generalJSON["OtherSkillsFromCV"].append(text)
    else:
      generalJSON["OtherSkillsFromCV"].append(text)
      break
    yPos = allWords[index]["positions"][0]["y"]
    index += 1


def addTextAndCheckSpaces(textLine, textToAdd):
  matchNoLeftSpace = constant.PATTERN_SYMBOL_NO_LEFT_SPACE.search(textToAdd)
  matchNoSpaces = constant.PATTERN_SYMBOL_NO_SPACES2.search(textToAdd)
  matchNoRightSpace = constant.PATTERN_SYMBOL_NO_RIGHT_SPACE.search(textToAdd)
  if matchNoLeftSpace is not None or matchNoSpaces is not None:
    # Jei randam [,/], pašalinam tarpą prieš jį
    textLine = textLine[:-1]

  textLine += textToAdd + " "

  if matchNoSpaces is not None or matchNoRightSpace is not None:
    # Po / irgi nereikia kablelio
    textLine = textLine[:-1]

  return textLine


def writeJSON(tmp_dir, cvFileName):
  with open(tmp_dir + '/' + os.path.splitext(cvFileName)[0] + ".json", "w") as dataFile:
    json.dump(generalJSON, dataFile)


def createGeneralJSON(tmp_dir, jsonPath, cvFileName):
  generalJSON["ID"] = ""
  generalJSON["Name"] = ""
  generalJSON["ContactInformation"] = ""
  generalJSON["Tel.No."] = ""
  generalJSON["EducationHistory"] = []
  generalJSON["EmploymentHistory"] = []
  generalJSON["Languages"] = []
  generalJSON["OtherSkillsFromCV"] = []
  generalJSON["Courses"] = []
  analyseRightCvPart(jsonPath[1])
  analyseLeftCvPart(jsonPath[0])
  writeJSON(tmp_dir, cvFileName)
  # print(generalJSON)

  return cvFileName + " completed successfully", multiplePositionsInfo

