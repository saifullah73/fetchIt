import xml.etree.ElementTree as etree
import time
import os


print("Note: the path must be entered with forward slashes")
pathWikiXML = input("Enter the path to the wiki XML file:\n")
current_directory = os.getcwd()
baseDirectory = os.path.join(current_directory, r'Repository/')    #directory for documents
if not os.path.exists(baseDirectory):
   os.makedirs(baseDirectory)
titleFile = open("titles.txt","w",encoding="UTF-8")       # document titles file


docId = 0                                           #counter to assing docIds to documents
totalCount = 0                                   #totalNo of pages found in dataset
articleCount = 0                                #couting all the valid articles/documents
title = None
start_time = time.time()
i=0
fileextension = 1
data= []


# Nicely formatted time string
def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)


#method to verify if current page being parsed qualifies as a document, i.e it is not a redirect page or a user page

def verifyOriginalArtical(pageElement):
    for pageElement in elem.iter():
        if strip_tag_name(pageElement) == "redirect":               #if tag is redirect we skip over the page
            return False
        elif strip_tag_name(pageElement) == "ns":                      #if ns(namespace !=0) we skip over page
            namespace = pageElement.text
            if namespace != "0":
                return False
    return True


# method to extract title and text of a document
def extractArticalData(pageElement):
    articleList = [" ", " "]
    for element in pageElement.iter():
        tagName = strip_tag_name(element)
        if tagName == "title":
            articleList[0] = element.text
        elif tagName == "text":
            articleList[1] = element.text
    data.append(articleList)

#method to write title of documents to file
def writeTitletofile(docId,title):

    titleFile.write(str(docId)+"-"+title+"\n")


# method to write 100 articels into a file with a prticular format
def writeArticlesToFile(data,filename):

    path = baseDirectory + filename + ".dat"
    file = open(path,'w',encoding="UTF-8")
    global docId
    for i in range(len(data)):
        temp = data[i]
        file.write("<page>\n")
        file.write("<docId>\n"+str(docId)+"\n")
        if temp[0] != None:
            file.write("<title>\n" + temp[0]+"\n")
            writeTitletofile(docId, temp[0])
        else:
            file.write("<title>\n" + " " + "\n</title>\n")
            writeTitletofile(docId, " ")
        if temp[1] != None:
            file.write("<text>\n" + temp[1] + "\n</text>\n")
        else:
            file.write("<text>\n" + " " + "\n</text>\n")
        docId = docId + 1
    file.close()
    del file


# method to clean tag of a page element
def strip_tag_name(element):
    tag = element.tag
    idx = k = tag.rfind("}")
    if idx != -1:
        tag = tag[idx + 1:]
    return tag



# parsing the dataset
for event, elem in etree.iterparse(pathWikiXML, events=('start', 'end')):
    tname = strip_tag_name(elem)
    if tname == "page" and event == 'end':      # a page is read completely
        totalCount = totalCount + 1
        if (totalCount % 1000 == 0):
            print("totalCount = " ,totalCount)
        if verifyOriginalArtical(elem):
            articleCount = articleCount + 1
            extractArticalData(elem)
            i = i + 1
            if i == 100:
                writeArticlesToFile(data, "d"+str(fileextension*100))
                fileextension = fileextension + 1
                data.clear()
                i = 0
        elem.clear()


writeArticlesToFile(data,"d"+str(fileextension*100))
data.clear()
titleFile.close()


elapsed_time = time.time() - start_time
print("Total pages: {:,}".format(totalCount))
print("Article pages: {:,}".format(articleCount))
print("Elapsed time: {}".format(hms_string(elapsed_time)))


