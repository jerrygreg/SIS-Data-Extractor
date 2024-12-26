import requests
import numpy as np

#Setting up the API call
#API calls should be prepended with API and appended with KEY
API = "https://sis.jhu.edu/api/classes/"
with open('Key.txt', 'r') as f: KEY = "?key="+f.readline()

#Defaults
#For CURRENTTERM use the following format
# "/(Season) (Year)"    if you want to specify
# "/current"            if you just want the current year
TERM = "/current"
DELIM1 = "_"
DELIM2 = ";"

#Dict of all availible schoolnames
ALLSCHOOLS = {
"BSPH"  : r"Bloomberg School of Public Health",
"CBS"   : r"Carey Business School",
"KSAS"  : r"Krieger School of Arts and Sciences",
"GKSAS" : r"Krieger School of Arts and Sciences Advanced Academic Programs",
"SAIS"  : r"Nitze School of Advanced International Studies",
"EDU"   : r"School of Education",
"NU"    : r"School of Nursing",
"PEA"   : r"The Peabody Institute",
"WSE"   : r"Whiting School of Engineering",
"GWSE"  : r"Whiting School of Engineering Programs for Professionals",
"PREPEA": r"The Peabody Preparatory",
"BSPHNC": r"Bloomberg School of Public Health Non-Credit",
"MED"   : r"School of Medicine",
}


def getData(schools = "all",term = TERM):
    pass


def writeData(data, outpath = "CourseData.txt", selections = "all", 
              delim1 = DELIM1, delim2 = DELIM2, 
              removecharacters = [], timeformat = "mins"):
    

    pass


if __name__ == "__main__":
    print("running as main")
    #data = getData(schools = "WSE,KSAS",term = "/current")
    #writeData(data)