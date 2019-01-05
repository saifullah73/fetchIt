import  zlib
from collections import *
import xml.etree.cElementTree as et
import re
import os
from Stemmer import Stemmer
import time



wikiFilePath = input("Please Enter path to wiki XML file :\n")
current_directory = os.getcwd()
baseDirectory = os.path.join(current_directory, r'TemporaryIndex/')
if not os.path.exists(baseDirectory):
   os.makedirs(baseDirectory)

start_time1 = time.time()
stemmer = Stemmer("english")
pattern = re.compile("[^a-zA-Z]")          # pattern for splitting text
stop_words = {}                                         # words that are not significant
stop_words_file = open("Stop_words.txt", "r")
content = stop_words_file.read()
content = re.split(",", content)
for word in content:
    if word:
        stop_words[word] = True



words_index = defaultdict(list)
inTitle = 0                                  # indicator for title hit
inSubTitle = 1                            # indicator for sub title hit
inCategory = 2                           # indicator for category hit
inText = 3                                  # indicator for text hit


pageCount = 0
file_count = 0
docCount = -1                             #counter to assign docIds
docs_per_file = 1000


#method to verify if current page being parsed qualifies as a document, i.e it is not a redirect page or a user page
def verifyOriginalArtical(pageElement):
    for pageElement in elem.iter():
        if strip_tag_name(pageElement) == "redirect":                #if tag is redirect we skip over the page
            return False
        elif strip_tag_name(pageElement) == "ns":                        #if ns(namespace) != 0 we skip the page
            namespace = pageElement.text
            if namespace != "0":
                return False
    return True


# Nicely formatted time string
def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)

# cleans unwanted information from text
def cleanText(text):

    tag = re.sub(r"{.*}", "", elem.tag)                                      # removing all data between {}
    text = re.sub(r"{{cite(.*?)}}","",text)                             # removing all citation data
    text = re.sub("\[\[Category:(.*?)\]\]","" ,text)            # removing all categories
    text = re.sub("== (.*?) ==", "", text)                                # removing all subtitle
    return text

#cleans page element tag
def strip_tag_name(element):
    tag = element.tag
    idx = k = tag.rfind("}")
    if idx != -1:
        tag = tag[idx + 1:]
    return tag



# writes hitlist of a word into a file
def writeWordToFile(word):
    arr = words_index[word]
    wordId = zlib.crc32(word.encode("UTF-8"))                                        #getting 4 bytes int id of word
    bWordId = wordId.to_bytes(4, byteorder="big", signed=False)        #reading first byte
    word_file = files[bWordId[0]]                                                                 #accessing the file corresponding to that file

    #constructing hitlist
    newline = word + "|"
    currentDoc = ""
    for e in arr:
        s = e.split(",")
        if s[0] == currentDoc:
            newline = newline + ("," + s[1] + "." + s[2])
        elif currentDoc == "":
            newline = newline + (s[0] + "-")
            newline = newline + (s[1] + "." + s[2])
        else:
            newline = newline + ("/" + s[0] + "-")
            newline = newline + (s[1] + "." + s[2])
        currentDoc = s[0]
    word_file.write(newline + "\n")



# method to extract title and text of a document
def extractArticalData(pageElement):
    for element in pageElement.iter():
        pagetag = strip_tag_name(element)
        if pagetag == "text":
            text = element.text
            try :
                #extracting and writing category hits
                tempword = re.findall("\[\[Category:(.*?)\]\]", text)
                categoryPos = 0
                if tempword:
                    for temp in tempword:
                        temp = re.split(pattern, temp)
                        for t in temp:
                            if t == "":
                                continue
                            t = t.lower()
                            t = stemmer.stemWord(t)
                            if t:
                                if t not in stop_words:
                                    if categoryPos > 65535:
                                        break
                                    words_index[t].append(str(docCount)+","+str(inCategory)+","+str(categoryPos))
                                    categoryPos = categoryPos + 1


            except :
                pass

            try:
                # extracting and writing subtitle hits
                tempword = re.findall("== (.*?) ==", text)
                subTitlePos = 0
                if tempword:
                    for temp in tempword:
                        temp = re.split(pattern, temp)
                        for t in temp:
                            if t == "":
                                continue
                            t = t.lower()
                            t = stemmer.stemWord(t)
                            if t:
                                if t not in stop_words:
                                    if subTitlePos > 65535:
                                        break
                                    words_index[t].append(str(docCount) + "," + str(inSubTitle) + "," + str(subTitlePos))
                                    subTitlePos = subTitlePos + 1


            except:
                pass

            try:
                # extracting and writing text hits
                    text = cleanText(text)
                    text = text.lower()
                    text = re.split(pattern, text)

                    pos = 0;
                    for word in text:
                        if word == "":
                            continue
                        if word:
                            if word not in stop_words:
                                word = stemmer.stemWord(word)
                                if pos > 65535:
                                    break
                                words_index[word].append(str(docCount) + "," + str(inText) + "," + str(pos))
                                pos = pos +1

            except:
                    pass

        if pagetag == "title":
            # extracting and writing title hits
            text = element.text
            try:
                text = text.lower()
                text = re.split(pattern, text)

                for pos,word in enumerate(text):
                    if word:
                        if word not in stop_words:
                            word = stemmer.stemWord(word)
                            words_index[word].append(str(docCount) + "," + str(inTitle) + "," + str(pos))
                            pos = pos + 1
            except:
                pass


#opeing all the 256 files for first byte range ( 0-255)
files = []
for i in range(256):
    file = open(baseDirectory+str(i)+".txt", 'a')
    files.append(file)


#parsing the dataset
for event, elem in et.iterparse(wikiFilePath, events=("start", "end")) :
    tag =  strip_tag_name(elem)
    if event == "start":
        if tag == "page" :
            pageCount = pageCount + 1
            text_words = {}

    if event == "end" and tag == "page":

        if verifyOriginalArtical(elem):
            docCount = docCount + 1
            print("documents Parsed = ",docCount)
            extractArticalData(elem)

            if ((docCount+1) % docs_per_file) == 0:     #writing hitlists if docs_per_file has been parsed
                for word in sorted(words_index):
                    writeWordToFile(word)
                words_index.clear()
        elem.clear()


for word in words_index:               #writing residual words
    writeWordToFile(word)

for i in range(256):
    files[i].close()


elapsed_time1 = time.time() - start_time1
print("Elapsed time for indexing : {}".format(hms_string(elapsed_time1)))

#starting to sort the temporary index barrels

start_time2 = time.time()
barrelWordList = defaultdict(dict)           # dictionary of dictionary to contain words and their hitlist in organized manner


current_directory = os.getcwd()
baseDirectory = os.path.join(current_directory, r'SortedIndex/')
if not os.path.exists(baseDirectory):
   os.makedirs(baseDirectory)


# method to get the final hitlist to be written into index
def getFinalWordIndex(newWord):
    wordDict =  barrelWordList[newWord]
    newline = str(word) + "|"
    for k , i in sorted(wordDict.items(), key=lambda kv: (len(kv[1]), kv[0]), reverse=True):
        newline = newline + str(k)+"-"+",".join(i) + "/"
    return (newline[:-1] +"\n")


#method to return word ID
def getWordId(word):
    wordId = zlib.crc32(word.encode("UTF-8"))
    return wordId


#   creating an organized reverse index for an unsorted barrel that may contain multiple word occurances
fl = open(current_directory+"/Lexicon.txt", "w")     # lexicon file to contain pointers of each word into the index
for i in range(256):
    f = open(current_directory+"/TemporaryIndex/"+str(i)+".txt", "r")  # opening a unsorted barrel for sorting
    for line in f:
        line = line[:-1]
        firstSplit = line.split("|")
        word = firstSplit[0]
        wordId = getWordId(word)
        secondSplit = firstSplit[1].split("/")
        for y in secondSplit:
            thirdsplit = y.split("-")
            z1 = thirdsplit[0]
            newArr=[]
            for z2 in thirdsplit[1].split(","):
                newArr.append(z2)
            if z1 in barrelWordList[wordId]:
                barrelWordList[wordId][z1].extend(newArr)     # if word is already recorded the dict extend its posting list by new posting list formed
            else:
                barrelWordList[wordId][z1] = newArr                # otherwise create a new posting list for it

    f = open(baseDirectory + str(i) + ".txt", "w")
    for word in sorted(barrelWordList):                               #writing the sorted barrel ( final reverse index )
        x = getFinalWordIndex(word)
        x1 = f.tell()                                                                      #getting word pointer in terms of offset
        fl.write(str(word)+"-"+str(x1)+"\n")                            #recording the word in lexicon
        f.write(x)
    print("Sorted ", i)
    barrelWordList.clear();
    f.close()

fl.close()

elapsed_time2 = time.time() - start_time2
elapsed_time = time.time() - start_time1
print("Elapsed time for sorting : {}".format(hms_string(elapsed_time2)))
print("Elapsed time for indexing : {}".format(hms_string(elapsed_time1)))
print("Elapsed time total : {}".format(hms_string(elapsed_time)))



