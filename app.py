# import required modules
import re
import requests
import pdfplumber
import json


# A function to download the pdf from the Texas A&M website with the given URL
def get_from_tamu(url):
    # use the last part of the url as the file name of the pdf
    localFileName = "./temp/"+url.split('/')[-1]
    with requests.get(url) as r:
        if(not r.status_code == 200):
            return -1
        with open(localFileName, 'wb') as f:
            f.write(r.content)
    return localFileName


def extractData(downloadedFile, year, sem):
    if (downloadedFile == -1):
        return []
    entries = []
    # process the pdf with pdfplumber
    with pdfplumber.open(downloadedFile) as pdf:

        for page in pdf.pages:
            text = page.extract_text()
            courseIdVendor = re.compile(r'\w{4}-\d{3}-\d{3}')

            for line in text.split('\n'):
                if courseIdVendor.match(line):
                    entry = line.split(" ")
                    entry = list(filter(lambda a: not a ==
                                        '' and not a == ' ', entry))
                    entryObj = {}
                    entryObj['courseId'] = entry[0][0:-4]
                    entryObj['year'] = year
                    entryObj['semester'] = ["SPRING", "SUMMER", "FALL"][sem-1]
                    entryObj['section'] = entry[0][-3:]
                    entryObj['letterGrades'] = list(
                        map(lambda a: float(a), entry[1:6]))
                    entryObj['totalGrades'] = float(entry[6])
                    entryObj['gpa'] = float(entry[7])
                    entryObj['professor'] = " ".join(entry[14:])
                    entries.append(entryObj)

    return entries


masterData = []

baseURL = "https://web-as.tamu.edu/GradeReports/PDFReports/"
# An array of all the abbreviations for each department
departments = ["AE", "AG", "AR", "AP", "GB", "BA", "DN", "DN_PROF",
    "ED", "EN", "GV", "GE", "LA", "MS", "NU", "CP_PROF", "PH", "QT", "SC"]

latestSem = 1
latestYear = 2020

# extract data from every single year
for i, department in enumerate(departments):
    # A variable to keep track of how many years back we have searched
    year = latestYear
    sem = latestSem
    while latestYear-year < 5:
        url = f"{baseURL}{year}{sem}/grd{year}{sem}{department}.pdf"
        masterData = masterData + extractData(get_from_tamu(url), year, sem)
        if(sem-1 < 1):
            sem = 3
            year -= 1
        else:
            sem -= 1  

    print(f"{str(i/len(departments)*100)}% done")
    print(f"\n  {len(masterData)} ")
    

        
        


# Ask the command line user for the url
# tamu_url = input("enter the url of the pdf: \n ")
# tamu_url = "https://web-as.tamu.edu/GradeReports/PDFReports/20201/grd20201EN.pdf"

# downloadedFile = get_from_tamu(tamu_url)
# entries = []


# output the data to a json file
with open('data.json', 'w') as outputFile:
    json.dump(masterData, outputFile)


# Saketh Rudraraju 2020
