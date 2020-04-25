import csv
import re
import os
import sys
from collections import Counter
from itertools import groupby
import string
import unicodedata
import concurrent.futures

# A slow but working script to run text sentiment on the given files
# @author Rolf Lewis (ralewis3)

# Set this to run analysis to build the custom lexicons for each class
runFullFrequencyAnalysis = 0
# Maps for the results of FFA
facultyWordMap = {}
courseWordMap = {}
staffWordMap = {}
projectWordMap = {}
studentWordMap = {}
departmentWordMap = {}

while (1):
    inDirName = input("Full Path to the input Directory:")
    # Local path is /Users/rolflewis/OneDrive/Documents/School/422/Project/Preprocessing/data/webkb

    if not (os.path.isdir(inDirName)):
        print("The value provided is not an existing directory. Try again.")
    else: 
        break
print("Directory set successfully.")

allFilePaths = []

topLevelDirs = [d for d in os.listdir(inDirName) if os.path.isdir(os.path.join(inDirName, d))]
for dir in topLevelDirs:
    secondLevelDirs = [d for d in os.listdir(os.path.join(inDirName, dir)) if os.path.isdir(os.path.join(inDirName, dir, d))]
    for secondDir in secondLevelDirs:
        finalFiles = [f for f in os.listdir(os.path.join(inDirName, dir, secondDir)) if os.path.isfile(os.path.join(inDirName, dir, secondDir, f))]
        for file in finalFiles:
            allFilePaths.append(os.path.join(inDirName, dir, secondDir, file))

print("There are", len(allFilePaths), "files in the given directory.")

print("Building Lexicons")

posLex = []
negLex = []
stopwords = []

with open('data/lexicons/lexicon.generic.positive.HuLiu.csv') as csvfile:
		posSentHuLiu = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in posSentHuLiu:
				posLex.append(row)

with open('data/lexicons/lexicon.finance.positive.LoughranMcDonald.csv') as csvfile:
		posSentLoughran = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in posSentLoughran:
				posLex.append(row)

with open('data/lexicons/lexicon.finance.positive.csv') as csvfile:
		posSent = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in posSent:
				posLex.append(row)

with open('data/lexicons/lexicon.generic.negative.HuLiu.csv', encoding='ISO-8859-1') as csvfile:
		negSentHuLiu = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in negSentHuLiu:
				negLex.append(row)
	
with open('data/lexicons/lexicon.finance.negative.LoughranMcDonald.csv') as csvfile:
		negSentLoughran = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in negSentLoughran:
				negLex.append(row)

with open('data/lexicons/lexicon.finance.negative.csv') as csvfile:
		negSent = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in negSent:
				negLex.append(row)

with open('data/stopwords/stopwords.finance.txt') as csvfile:
		stopwrds = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in stopwrds:
				stopwords.append(row)

with open('data/stopwords/stopwords.generic.txt') as csvfile:
		stopwrds = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in stopwrds:
				stopwords.append(row)

with open('data/stopwords/stopwords.geographic.txt') as csvfile:
		stopwrds = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in stopwrds:
				stopwords.append(row)

with open('data/stopwords/stopwords.names.txt') as csvfile:
		stopwrds = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in stopwrds:
				stopwords.append(row)
				
for row in posLex:
		row[0] = row[0].lower()		
posLex = [k for k in groupby(sorted(posLex))]
for row in negLex:
		row[0] = row[0].lower()
negLex = [k for k in groupby(sorted(negLex))]
for row in stopwords:
		row[0] = row[0].lower()
stopwords = [k for k in groupby(sorted(stopwords))]

distinctPosLex = []
for row in posLex:
		distinctPosLex.append((row[0][0]).lower())
distinctNegLex = []
for row in negLex:
		distinctNegLex.append((row[0][0]).lower())
distinctStopwords = []
for row in stopwords:
		distinctStopwords.append((row[0][0]).lower())
		
posLex = distinctPosLex
negLex = distinctNegLex 
stopwords = distinctStopwords

# Create the per-classification lists of identifying words
# These are made from taking the the top 15 non-trivial words from the CSVs for each class created by running the Full Frequency Analysis portion of this code.
# We are removing any words that appear in all of the lexicons.
courseTriggers = ['course', 'homework', 'programming', 'class', 'information', 'lecture', 'office', 'assignment', 'cs', 'project', 'assignments', 'due', 'final', 'exam', 'hours:']
deptTriggers = ['department','information','university','research','graduate','faculty','web','undergraduate','computing','about','courses','student','course','engineering','server']
facTriggers = ['research', 'university','professor','systems','department','information','parallel','software','programming','engineering','computing','distributed','conference','international','system']
projectTriggers = ['research','project','university','group','systems','information','system','parallel','software','laboratory','data','distributed','design','computing','performance']
staffTriggers = ['research','university','department','information','parallel','system','systems','software','web','about','project','work', 'distributed', 'computing', 'technical']
studentTriggers = ['university', 'research', 'department', 'information', 'student', 'about', 'graduate', 'web', 'links', 'systems', 'interests', 'software', 'engineering','working','work']

# Calculates the sentiment score for each page based on the positive and negative lexicons.
def scoreSentiment(tokens, posLex, negLex):
    sentScore = 0
    for word in tokens:
            if word.lower() in stopwords:
                continue
            if word.lower() in posLex:
                sentScore = sentScore + 1
            elif word.lower() in negLex:
                sentScore = sentScore - 1
    return sentScore

# Calculates the varety of words in each page. Returns the number of unique words.
def linguisticVariety(tokens):
    words = []
    for word in tokens:
        if word not in words:
            words.append(word)
    return len(words)

# Calculates the average word length for each page's text
def avgWordLength(tokens):
    sumLengths = 0
    for word in tokens:
        sumLengths = sumLengths + len(word)
    return sumLengths / len(tokens)

# Scores the pages based on the custom lexicons for each class
def scoreTriggers(triggers, tokens):
    score = 0
    for word in tokens:
        if word.lower() in triggers:
            score = score + 1
    return score

# Detects and skips any content that comes before a HTML or HEAD opening tag, whichever comes first.
# Defaults to removing first five lines as a fallback if header cannot be detected.
def prepareFile(file, encodingParam):
    # Open the file for reading
    with open(os.path.join(file), 'r', encoding=encodingParam) as webpage:
        fullWebPageData = webpage.read()
        lines = fullWebPageData.splitlines(True)
        # Track the page data as it is collected
        data = ''
        found = False
        mimeHeaderCutoff = 0
        tagFinder = re.compile('^<\S*>')
        for line in lines:
            finds = re.findall(tagFinder, line)
            if len(finds) != 0:
                found = True
                break
            mimeHeaderCutoff = mimeHeaderCutoff + 1

        if found == False:
            mimeHeaderCutoff = 5

        # Read all lines after the calculated header
        for line in lines[mimeHeaderCutoff:]:
            data = data + line

        cleanTags = re.compile('<.*?>')
        # Process until processing makes no changes
        while (1):
            # Take all tags out
            old = data
            data = re.sub(cleanTags, '', data)
            # If no tags were left to be removed
            if old == data:
                noTagsData = data
                break
        # Return all page states needed for analysis
        return [fullWebPageData, noTagsData]

# Runs all analysis steps for a given files. Uses helper functions above.
def analyze(file):
    fullWebPageData = ''
    noTagsData = ''
    tokenizedPage = ''

    pageStates = []
    try:
        pageStates = prepareFile(file, encodingParam="utf-8")
    except UnicodeDecodeError:
        pageStates = prepareFile(file, encodingParam="ISO-8859-1")
    fullWebPageData = pageStates[0]
    noTagsData = pageStates[1]

    tokenizedPage = noTagsData.split()

    for token in tokenizedPage:
        token = token.lower()

    score = scoreSentiment(tokenizedPage, posLex, negLex)
    langVariety = linguisticVariety(tokenizedPage) / len(tokenizedPage)
    avgWordLen = avgWordLength(tokenizedPage)

    courseTRG = scoreTriggers(courseTriggers, tokenizedPage)
    facTRG = scoreTriggers(facTriggers, tokenizedPage)
    staffTRG = scoreTriggers(staffTriggers, tokenizedPage)
    deptTRG = scoreTriggers(deptTriggers, tokenizedPage)
    proTRG = scoreTriggers(projectTriggers, tokenizedPage)
    stuTRG = scoreTriggers(studentTriggers, tokenizedPage)

    lineCount = len(fullWebPageData.splitlines())
    wordCount = len(tokenizedPage)

    tagFinder = re.compile('<.*?>')
    tagList = re.findall(tagFinder, fullWebPageData)
    tagSet = set(tagList)
    uniqueTags = len(tagSet)
    tagCount = len(tagList)
    tagVariety = uniqueTags / tagCount

    imageFinder = re.compile('<img .*>')
    imageCount = len(re.findall(imageFinder, fullWebPageData))

    linkFinder = re.compile('<a href=.*>')
    links = re.findall(linkFinder, fullWebPageData)

    emailFinder = re.compile('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
    emails = re.findall(emailFinder, fullWebPageData)
    emailCount = len(emails)
    linkCount = 0
    for link in links:
        if 'mailto:' not in link:
            linkCount = linkCount + 1

    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    weekdayCount = 0
    for weekday in weekdays:
        weekdayFinder = re.compile('' + weekday)
        finds = re.findall(weekdayFinder, fullWebPageData)
        weekdayCount = weekdayCount + len(finds)

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
    monthCount = 0
    for month in months:
        monthFinder = re.compile('' + month)
        finds = re.findall(monthFinder, fullWebPageData)
        monthCount = monthCount + len(finds)

    recType = ''
    if '/course/' in file:
        recType = 'course'
    elif '/department/' in file:
        recType = 'department'
    elif '/faculty/' in file:
        recType = 'faculty'
    elif '/other/' in file:
        recType = 'other'
    elif '/project/' in file:
        recType = 'project'
    elif '/staff/' in file:
        recType = 'staff'
    elif '/student/' in file:
        recType = 'student'

    school = ''
    if '/cornell/' in file:
        school = 'Cornell'
    elif '/misc/' in file:
        school = 'misc'
    elif '/texas/' in file:
        school = 'Texas'
    elif '/washington/' in file:
        school = 'Washington'
    elif '/wisconsin/' in file:
        school = 'Wisconsin'

    lastSlashIndex = file.rfind('/')

    row = [file[int(lastSlashIndex) + 1:], recType, school, score, lineCount, wordCount, langVariety, avgWordLen, tagCount, uniqueTags, tagVariety, imageCount, emailCount, linkCount, weekdayCount, monthCount, courseTRG, deptTRG, facTRG, staffTRG, proTRG, stuTRG]
    print(row)
    with open(os.path.join(inDirName, 'out.csv'),'a') as fd:
        writer = csv.writer(fd)
        writer.writerow(row)

def fullFrequencyAnalysis(file):
    global courseWordMap
    global studentWordMap
    global departmentWordMap
    global facultyWordMap
    global staffWordMap
    global projectWordMap

    fullWebPageData = ''
    noTagsData = ''
    tokenizedPage = ''

    pageStates = []
    try:
        pageStates = prepareFile(file, encodingParam="utf-8")
    except UnicodeDecodeError:
        pageStates = prepareFile(file, encodingParam="ISO-8859-1")
    fullWebPageData = pageStates[0]
    noTagsData = pageStates[1]
    tokenizedPage = noTagsData.split()

    for token in tokenizedPage:
        if (token.lower() in stopwords):
            continue
        if ('/course/' in file):
            if (token.lower() in courseWordMap):
                courseWordMap[token.lower()] = courseWordMap[token.lower()] + 1
            else:
                courseWordMap[token.lower()] = 1
        elif ('/student/' in file):
            if (token.lower() in studentWordMap):
                studentWordMap[token.lower()] = studentWordMap[token.lower()] + 1
            else:
                studentWordMap[token.lower()] = 1
        elif ('/department/' in file):
            if (token.lower() in departmentWordMap):
                departmentWordMap[token.lower()] = departmentWordMap[token.lower()] + 1
            else:
                departmentWordMap[token.lower()] = 1
        elif ('/faculty/' in file):
            if (token.lower() in facultyWordMap):
                facultyWordMap[token.lower()] = facultyWordMap[token.lower()] + 1
            else:
                facultyWordMap[token.lower()] = 1
        elif ('/staff/' in file):
            if (token.lower() in staffWordMap):
                staffWordMap[token.lower()] = staffWordMap[token.lower()] + 1
            else:
                staffWordMap[token.lower()] = 1
        elif ('/project/' in file):
            if (token.lower() in projectWordMap):
                projectWordMap[token.lower()] = projectWordMap[token.lower()] + 1
            else:
                projectWordMap[token.lower()] = 1
    print(file)

if runFullFrequencyAnalysis == 1:
    # Build worker threads and process the file pool
    # using threads here because of need for global maps
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for file in allFilePaths:
            executor.submit(fullFrequencyAnalysis, (file))

    with open(os.path.join(inDirName, 'courseFreq.csv'),'w') as fd:
        print(courseWordMap)
        writer = csv.writer(fd)
        for key in courseWordMap:
            row = [key, courseWordMap[key]]
            writer.writerow(row)

    with open(os.path.join(inDirName, 'studentFreq.csv'),'w') as fd:
        writer = csv.writer(fd)
        for key in studentWordMap:
            row = [key, studentWordMap[key]]
            writer.writerow(row)
    
    with open(os.path.join(inDirName, 'departmentFreq.csv'),'w') as fd:
        writer = csv.writer(fd)
        for key in departmentWordMap:
            row = [key, departmentWordMap[key]]
            writer.writerow(row)

    with open(os.path.join(inDirName, 'facultyFreq.csv'),'w') as fd:
        writer = csv.writer(fd)
        for key in facultyWordMap:
            row = [key, facultyWordMap[key]]
            writer.writerow(row)

    with open(os.path.join(inDirName, 'staffFreq.csv'),'w') as fd:
        writer = csv.writer(fd)
        for key in staffWordMap:
            row = [key, staffWordMap[key]]
            writer.writerow(row)

    with open(os.path.join(inDirName, 'projectFreq.csv'),'w') as fd:
        writer = csv.writer(fd)
        for key in projectWordMap:
            row = [key, projectWordMap[key]]
            writer.writerow(row)
else:
    # Build worker processes and process the fileList pool
    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
        executor.map(analyze, allFilePaths)