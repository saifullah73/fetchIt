from tkinter import *
import Searcher
import time




def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)

# method to fetch a document from doc ID
def fetchDoc(docId):
    if docId < 100:
        x = "100"
    elif len(str(docId)) > 3:
        if (str(docId)[-3:-2]) != "9":
            x = str(docId)[:-3] + str(int(str(docId)[-3:-2]) + 1) + "0" + "0"
        else:
            x = (str(docId))[:-4] + str(int(str(docId)[-4:-3]) + 1) + "0" * 3

    else:
        if str(docId)[:-3] != "9":
            x = str(int(str(docId)[-3:-2]) + 1) + "0" + "0"
        else:
            x = "1000"
    f = open("D://Engine/Document2/d" + str(x) + ".dat", encoding="UTF-8")
    for line in f:
        line = line[:-1]
        if line == "<docId>":
            if f.readline()[:-1] == str(docId):
                f.readline()
                title = f.readline()[:-1]
                f.readline()
                y = f.readline()[:-1]
                text = []
                while y != "</text>":
                    text.append(y)
                    y = f.readline()[:-1]
                f.close()
                return title,text

# ListItemClickEvent
def onselect(evt):
    w = evt.widget
    index = int(w.curselection()[0])
    title,text = fetchDoc(docIds[index])
    documentWindow(title,text)

#button Event
def fetch_it():
    text = text1.get()
    root.withdraw()
    getResultsWindow(text)

#button Event
def research():
    root.deiconify()
    root.state("zoomed")
    window.destroy()





#single document display window
def documentWindow(title,text):
    window = Tk("")
    window.title(title)
    window.state("zoomed")
    Label(window, text="Title:", font="Courier 25 bold italic", fg="orange").pack()
    Label(window, text=" ").pack()
    Label(window, text= title , font="Courier 30 bold italic", fg="orange").pack()
    Label(window, text=" ").pack()
    frame = Frame(window)
    frame.pack()
    scrollbar = Scrollbar(frame, orient="vertical")
    scrollbar1 = Scrollbar(frame, orient="horizontal")
    scrollbar.pack(side="right", fill="y")
    scrollbar1.pack(side="bottom", fill="x")
    listNodes = Listbox(frame, width=210, height=500, font=("Times", 12), yscrollcommand=scrollbar.set,xscrollcommand=scrollbar1.set)
    listNodes.bind('<<ListboxSelect>>')
    listNodes.pack(side="left", fill="y")
    scrollbar.config(command=listNodes.yview)
    scrollbar1.config(command=listNodes.xview)
    for i in text:
        listNodes.insert(END,i)
    window.mainloop()

#results window
def getResultsWindow(text):

    global docIds
    start_time = time.time()
    results = s.doQuery(text)
    docIds = [x for x in results.keys()]
    totalResults = len(results)
    global window
    window = Tk("")
    window.title("Results")
    window.state("zoomed")
    Label(window, text="Results",font ="Courier 40 bold italic",fg = "orange",height = 2).pack()
    elapsed_time = time.time() - start_time
    totalTime = format("Query Time: {}".format(hms_string(elapsed_time)))
    metaText = "Total Results = " + str(totalResults) + "\n" + totalTime + "s"
    Label(window,text = metaText).place(x=1760,y=100)
    Button(window, text="Back",command = research, height=1, width=5, bg = "red", fg = "white",font="Times 10 ").place(x=0,y=0)
    frame = Frame(window)
    frame.pack()
    listNodes = Listbox(frame, width=210, height=500 , font=("Times", 12))
    listNodes.bind('<<ListboxSelect>>', onselect)
    listNodes.pack(side="left", fill="y")
    scrollbar = Scrollbar(frame, orient="vertical")
    scrollbar.config(command=listNodes.yview)
    scrollbar.pack(side="right", fill="y")
    listNodes.config(yscrollcommand=scrollbar.set)


    if len(results) == 0:
        listNodes.insert(END,"No results Found.........")
    else:
        for a, b in results.items():
            listNodes.insert(END, "Title :  " + str(b))

    window.mainloop()



if __name__=="__main__":
    s = Searcher.Searcher()
    docID = []

    # home page
    root = Tk()
    root.title('FETCH IT')
    root.state("zoomed")
    root.config(background='white')
    frame1 = Frame(root, bg='white')
    text1 = StringVar()
    img = PhotoImage(file="logo.png")
    panel = Label(frame1, image=img, borderwidth=0, highlightthickness=0)
    panel.pack(side="top", pady=70)
    titleLabel = Label(frame1, text="fetch it", fg="orange", bg="white", font="Courier 40 bold italic",height = 1,underline = 0).pack()
    textentry = Entry(frame1, textvariable=text1, width=30, font="Helvetica 12").pack(ipady=5)
    button1 = Button(frame1, text="Fetch It", command =fetch_it , height=2, width=10, activebackground = "orange",font = "Courier 10 bold").pack()
    frame1.pack(fill='both', expand='yes')
    root.mainloop()













