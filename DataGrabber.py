import requests
import numpy as np

#TODO: CHANGE TO USE ADVANCED SEARCH

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
DEBUG = True

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


def getFullJson(schools = "ALL", term = TERM, debug = DEBUG):
    """
    ----------------------------------------------------
    Gets all the data from SIS
    Returns a long dictionary format just like SIS
    ----------------------------------------------------
    ----------------------------------------------------
    ARGUMENTS:
    - schools: The schools to search through
    "ALL"   
        Searches all JHU schools - DEFAULT
    "WSE,KSAS,SAIS,PEA,PREPEA,BSPH,CBS,GKSAS,GWSE,EDU,NU,BSPHNC,MED"    
        Use any subset of these options to specify schools

    - term: 
    "/(Season) (Year)"    
        if you want to specify. E.g. "/Fall 2024"
    "/current"            
        if you just want the current semester
    
    - debug:
    True
        Prints debug info
    False
        doesn't pring debug info
    ----------------------------------------------------
    """
    #Get school_list
    school_list = getSchoolList(schools = schools,debug = debug)
    
    #Load in all data
    if debug: print(f"Getting all courses from: {school_list}")
    basicJson = getBasicJson(school_list, term = term, debug = debug)
    sectioncodes = getSectionCodes(basicJson, debug = debug)

    # change term for the advancedjson function
    term = "/" + basicJson[0]["Term"]
    fullJson = getAdvancedJson(sectioncodes, term = term, debug = debug)

    return fullJson

def getSchoolList(schools = "ALL", debug = DEBUG):
    #Load global variables
    global ALLSCHOOLS

    #Match based on schools
    # I like match case as it allows easy changing cases
    match schools.upper():
        case "ALL": #Go through all schools
            school_list = np.array(ALLSCHOOLS.values())

        case _:     #Default
            schools_keys = np.array(schools.split(","))

            #ERROR CHECKING
            # this is to check if all the schools input are valid
            checkkeys = np.isin(schools_keys, list(ALLSCHOOLS.keys()))
            if False in checkkeys:
                raise KeyError(f"The following schools are invalid inputs: {schools_keys[~checkkeys]}")

            school_list = np.array([ALLSCHOOLS[key] for key in schools_keys])
    return school_list

def getBasicJson(school_list, term = TERM, debug = DEBUG):
    """
    Returns the basicJson
    i.e. a list of dictionaries that is the straight output from the SIS api
    """
    #Load Globals
    global API
    global KEY

    #init
    basicjson = []
    term = term.replace(" ","%20")

    #Loop through schools and get all courses from each
    for school in school_list:
        if debug: print(f"Getting courses from: {school}")

        school = school.replace(" ","%20") #Correct so it works as a link properly
        #Request the json for the school
        # grabs all the classes in that school in that term
        r = requests.get(API + school + term + KEY)
        rj = r.json()
        basicjson.extend(rj)

    return basicjson

def getSectionCodes(basicJson, debug = DEBUG):
    """
    Returns the section codes in an array
    Takes a basicJson as an input
    """
    #Loop through basicJSON to grab the section names and coursecode of each one
    sectioncodes = np.full(len(basicJson)," "*10)
    for i, courseJson in enumerate(basicJson):
        section = courseJson["SectionName"]                         #E.g. 01
        coursecode = "".join(courseJson["OfferingName"].split(".")) #E.g. EN520219
        sectioncode = coursecode+section #This is needed because for a SIS request we need both the section and coursecode

        sectioncodes[i] = sectioncode

    #ERROR CHECKING
    # this is to check if all the courses are looped over and all section codes are found
    if " "*10 in sectioncodes:
        not_grabbed = np.where(0 in sectioncodes == True)
        raise ValueError(f"Section codes for classes at indexes not grabbed: {not_grabbed}")

    return sectioncodes

def getAdvancedJson(sectioncodes, term = "/Fall 2024", debug = DEBUG):
    """
    Returns json with section data
    uses the section codes as input
    e.g. ["EN52021901","AS17311702",...]

    !!term default is Fall 2024!!
    """
    #Load globals
    global API
    global KEY

    #init 
    advancedJson = []
    term = term.replace(" ","%20")

    #loop through codes
    for i,code in enumerate(sectioncodes):
        if debug: print(f"{i}) Getting {code[:2]+"."+code[2:5]+"."+code[5:8]} : {code}...")

        r = requests.get(API + code + term + KEY)
        rj = r.json()
        advancedJson.extend(rj)

        #ERROR CHECKING
        # this is checking for jsons that are returned with less or more than one returned course
        # i.e. nonsensical returns (Possibly a class that doesnt exist)
        if len(rj) != 1:
            if debug: print(f"ERROR: Data for {code} has length {len(rj)}")
            continue 

    return advancedJson[:]

def writeData(fullJson, outpath = "CourseData.txt", selections = "all", 
              delim1 = DELIM1, delim2 = DELIM2, removecharacters = [], 
              timeformat = "mins", fileformat = "delimed"):
    """
    ----------------------------------------------------
    Writes data to a text file
    This helps in allowing you to access this data quickly without having to request from the API repeatedly
    ----------------------------------------------------
    ----------------------------------------------------
    ARGUMENTS:
    - fullJson
        The Json with all the data that you want to parse and write to a file
        Must be formatted just like SIS API json returns

    - outpath
        The filepath to save the text file to

    - selections

    - delim1

    - delim2

    - removecharacters

    - timeformat

    - fileformat
    ----------------------------------------------------
    """

    with open(outpath,"w") as outfile:
        pass

    pass


if __name__ == "__main__":
    print("running as main")
    fullJson = getFullJson(schools = "WSE,KSAS",term = "/current")
    #writeData(data)
    print("done")