import zlib
from Stemmer import Stemmer
import time
import re
from collections import *
import math





class Searcher:

    def __init__(self):
        self.lexicon = {}            #lexicon for assisting in search
        self.titles = {}                #document titles
        self.stop_words = {}
        self.stemmer = Stemmer("english")  # for stemming of words
        self.totalDocs = 127467                     # total counts of all pages found in our document ( please update this count according to your dataset)
        self.load()

# loading all the files and writing them to respective dictionaries
    def load(self):
        self.loadLexicon("Lexicon.txt")
        self.loadTitles("titles.txt")
        self.loadStopWords("Stop_words.txt")

    def loadLexicon(self, path):
        try:
            lexiconFile = open(path, 'r')
            for line in lexiconFile:
                x = line[:-1].split("-")
                self.lexicon[int(x[0])] = int(x[1])
        except:
            print("Error opening lexicon file")
            sys.exit(0)

    def loadTitles(self , path):
        try:
            titleFile = open(path, 'r',encoding="UTF-8")
            for line in titleFile:
                x= line[:-1].split("-")
                self.titles[int(x[0])] = x[1]
        except:
            print("Error opening titles file")
            sys.exit(0)

    def loadStopWords(self, path):
        try:
            stop_words_file = open(path, 'r')
            content = stop_words_file.read()
            content = re.split(",", content)
            for word in content:
                if word:
                    self.stop_words[word] = True
        except:
            print("Error opening stop words file")
            sys.exit(0)

    # method to intersect lists
    def intersectLists(self, lists):
        if len(lists) == 0:
            return []
        # start intersecting from the smaller list
        lists.sort(key=len)
        c = lists[0]
        for x in lists[1:]:
            c = list(set(c) & set(x))
        return c

    #method to get document titles for document ids
    def getDocTitles(self, docIds):
        docTitles = []
        for y in docIds:
            title = self.titles.get(y)
            if title != None:
                docTitles.append(title)
        return  docTitles

#method to process and organize raw hitlist from index
    def processRawHitlist(self, hitlists):
        parentArr=[]                            # master array to contain all categories of hits
        parentArr.append({})               # title hits dictionary
        parentArr.append({})               # subTitle hits dictionary
        parentArr.append({})                # category hits dictionay
        parentArr.append({})                # text hit dictionary

        # splitting the hitlist and recording hits in parentArr
        hitlists = hitlists[:-1].split("|")[1].split("/")
        for singleList in hitlists:
            singleDocumentList = singleList.split("-")
            docId = int(singleDocumentList[0])
            for smallerLists in  singleDocumentList[1].split(","):
                a = smallerLists.split(".")
                type = int(a[0])     # the category or type of hit(title, text,etc)
                pos = int(a[1])
                if docId not in parentArr[type]:
                    parentArr[type][docId] = [pos]
                else:
                    parentArr[type][docId].append(pos)
        return parentArr

# method to return final processed hitlist of a word
    def getHitlist(self, word):
        word = word.lower()
        wordId = zlib.crc32(word.encode("UTF-8"))                    # getting word id
        bWordId = wordId.to_bytes(4, byteorder="big", signed=False)
        self.word_file = bWordId[0]             # getting the file containing the word
        off = self.lexicon.get(wordId)          # getting word pointer in index
        if off != None:
            f = open("SortedIndex/" + str(bWordId[0]) + ".txt", "r")
            f.seek(off)
            y = f.readline()              # reading raw hitlist
            f.close()
            return self.processRawHitlist(y)

        else:
            return []


# method to return all docs that contain the given words without catering for proximity
    def getUnproximatedDocs(self, wordsList,type):

        docIds = []
        for arr in wordsList:
            if arr != []:
                arr = arr[type]
                docIds.append(arr.keys())
        docs = self.intersectLists(docIds)
        return docs

# method to do return phrase results in a particular type
    def getResultsForPhrase(self,wordsList, type):
        termDocsCount = 0
        docs = {}
        unproximatedDocs = self.getUnproximatedDocs(wordsList,type)
        # converting unproximated docs to proximated
        for docId in unproximatedDocs:
            proximityArr = []
            for i, arr in enumerate(wordsList):
                if arr != []:
                    arr = arr[type]                     #getting hitlist for a particular type of hits
                    poss = arr.get(docId)
                    proximityArr.append([pos - i for pos in poss])      # subtracting n from positions of a word in document to bring them on a common line
            t = self.intersectLists(proximityArr)                              #intersecting positions to find phrases in documents
            if (len(t) > 0):
                tf = len(t)                                                                        # term frequency would be the length of insersection result
                docs[docId] = tf                                                            #recording term frequency of each document
                termDocsCount +=1
        if type == 3:
            return self.rankDocs(docs,termDocsCount)                   # ranking the results
        else:
            return docs.keys()


    def rankDocs(self,docs,termDocsCount):
        y = docs
        #calculating the inverse document frequency
        if termDocsCount != 0:
            x = self.totalDocs/termDocsCount
            ifd = math.log2(x)

        # calculating tf-idf score for each document
            for x in docs.keys():
                docs[x] = docs[x]*ifd

        # returning sorted array based of tf-tdf values of documents
            x = sorted(docs.items(), key=lambda kv: kv[1],reverse=True)
            y = [a[0] for a in x]

        return y



# append two arrays
    def appendResults(self,results,moreResults):

        for x in moreResults:
            if x not in results:
                results.append(x)
        return results


# get results for a single word query
    def getResultsForWord(self,wordHitlist,type):

        docs={}
        typeArr = wordHitlist[type]                              #getting hitlists for particular type of hit
        for doc in typeArr:
            docs[doc] = len(typeArr.get(doc))                # recording tf of documents relative to query term
        termDocsCount = len(typeArr)
        if type == 3 and termDocsCount != 0:                #ranking title,categories,subtitles has no significant benefits
            x = self.totalDocs / termDocsCount
            ifd = math.log2(x)
            for x in docs.keys():
                docs[x] = docs[x] * ifd                            #finding tf- idf scores
            x = sorted(docs.items(), key=lambda kv: kv[1], reverse=True)       # sorting by tf-idf scores
            y = [a[0] for a in x]
            return y
        else:
            return [x for x in docs.keys()]


# method to do single word query on words of a phrase query and return results with a certain order
    def  getMoreResults(self,singleWordResults , count):

        docs = []
        for type in range(4):
            a = []
            maxCount = -1
            for i in range(len(singleWordResults)):
                v = singleWordResults[i].get(type)
                if v == None:
                    continue
                if len(v) > maxCount:
                    maxCount = len(v)
                a.append(v)

            for j in range(maxCount):
                for i in range(len(a)):
                    if j < len(a[i]):
                        docs.append(a[i][j])
                        if len(docs) == count:
                            return docs



# method to do one word query
    def oneWordQuery(self,word,mode):
        hitlist = self.getHitlist(word)
        if hitlist == []:
            return {}
        else:
            if mode:             # either an atomic single word query or a single word query on terms of a phrase word query
                results = {}   #dictionary results for query on terms of phrase query to allow order
                titleDoc =   self.getResultsForWord(hitlist,0)
                results[0] = titleDoc # results for title hits

                subTitleDoc = self.getResultsForWord(hitlist,1)
                results[1] = subTitleDoc # results for sub title hits

                categoryDoc = self.getResultsForWord(hitlist, 2)
                results[2] = categoryDoc    # results for category hits

                textDoc = self.getResultsForWord(hitlist,3)
                results[3] = textDoc    #results for text hits

                return results

            else:
                results = []  # array results for query on an atomic single word
                titleDoc = self.getResultsForWord(hitlist, 0)
                results = self.appendResults(results,titleDoc)

                subTitleDoc = self.getResultsForWord(hitlist, 1)
                results = self.appendResults(results,subTitleDoc)

                categoryDoc = self.getResultsForWord(hitlist, 2)
                results = self.appendResults(results,categoryDoc)

                textDoc = self.getResultsForWord(hitlist, 3)
                results = self.appendResults(results,textDoc)

                return results






#method to do a phrase query
    def phraseQuery(self,words):

        results = []
        wordsList=[]
        for word in words:
            wordsList.append(self.getHitlist(word))

        titleDoc =   self.getResultsForPhrase(wordsList,0)   # title hit results
        results = self.appendResults(results ,titleDoc)
        subTitleDoc = self.getResultsForPhrase(wordsList,1) # subtitle hit results
        results = self.appendResults(results,subTitleDoc)

        categoryDoc = self.getResultsForPhrase(wordsList, 2) # category hit results
        results =self.appendResults(results,categoryDoc)

        textDoc = self.getResultsForPhrase(wordsList,3) # text hit results
        results =self.appendResults(results,textDoc)

# doing a query on terms of a phrase with limit of 300 more results
        if len(results) < 300:
            singleWordResults = []
            for word in words:
                singleWordResults.append(self.oneWordQuery(word,True))
            y = 50 - len(results)
            x = self.getMoreResults(singleWordResults,y)
            if x != None:
                results += x

        return results





# parent query method and classifier
    def doQuery(self,words):

        results = {}
        queryWord=[]
        words = words.strip().split(" ")
        for word in words:
            word = word.lower()
            word = self.stemmer.stemWord(word)
            if word not in self.stop_words:
                queryWord.append(word)

        if len(queryWord) == 0:
            return {}

        elif len(queryWord) > 1:
            docIds = self.phraseQuery(queryWord)
            for id in docIds:
                results[id] = self.titles.get(id)

        else:
            docIds = self.oneWordQuery(queryWord[0], False)
            for id in docIds:
                results[id] = self.titles.get(id)

        return results



# Nicely formatted time string
def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)


if __name__=="__main__":
    newSearch = Searcher()
    print("Please Wait while the files are loaded")
    words = input ("Please enter the query: ")
    start_time = time.time()
    results = newSearch.doQuery(words)
    for a,b in results.items():
        print(a, end="  ")
        print(b)
    print("Total Results = ",len(results))
    elapsed_time = time.time() - start_time
    print("Elapsed time: {}".format(hms_string(elapsed_time)))











