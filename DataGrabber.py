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
DELIM1 = ";"
DELIM2 = "_"
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


def getFullJson(schools = "all", term = TERM, debug = DEBUG):
    """
    ----------------------------------------------------
    Gets all the data from SIS
    ----------------------------------------------------

    Returns a long dictionary format just like SIS
    
    ----------------------------------------------------
    ARGUMENTS:
    - schools: The schools to search through    
    
    "all" Searches all JHU schools - DEFAULT

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
    "MED"   : r"School of Medicine"

    Use any subset of these options to specify schools

    - term: 

    "/(Season) (Year)"    
        if you want to specify. E.g. "/Fall 2024"

    "/current"            
        if you just want the current semester
    
    - debug:

    True,
        Prints debug info

    False,
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

def getSchoolList(schools = "all", debug = DEBUG):
    """
    ----------------------------------------------------
    Grabs the schools list from school names from the codes of the school names
    ----------------------------------------------------

    Can specify any number of schools using their shortened codes comma delimited

    ----------------------------------------------------
    ARGUMENTS:
    - schools: The schools to search through    
    
    "all" Searches all JHU schools - DEFAULT

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
    "MED"   : r"School of Medicine"

    Use any subset of these options to specify schools
    """
    #Load global variables
    global ALLSCHOOLS

    #Match based on schools
    # I like match case as it allows easy changing cases
    match schools.upper():
        case "all": #Go through all schools
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
    ----------------------------------------------------
    Returns the basicJson
    ----------------------------------------------------
    
    i.e. a list of dictionaries that is the straight output from the SIS api

    ----------------------------------------------------
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
    ----------------------------------------------------
    Returns the section codes in an array
    ----------------------------------------------------

    Takes a basicJson as an input

    ----------------------------------------------------
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
    ----------------------------------------------------
    Returns json with section data
    ----------------------------------------------------
    
    uses the section codes as input
    e.g. ["EN52021901","AS17311702",...]

    ----------------------------------------------------

    !!term default is Fall 2024!!
    ----------------------------------------------------
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
              fileformat = "delimed", debug = DEBUG):
    """
    ----------------------------------------------------
    Writes data to a text file
    ----------------------------------------------------

    This helps in allowing you to access this data quickly without having to request from the API repeatedly
    
    ----------------------------------------------------
    ARGUMENTS:
    - fullJson:
        The Json with all the data that you want to parse and write to a file
        Must be formatted just like SIS API json returns

    - outpath:
        The filepath to save the text file to

    - selections:
        Comma delimited string containing all the data you want write to the file

        POSSIBLE SELECTIONS

        'TermStartDate', 'SchoolName', 'CoursePrefix', 'Term', 'Term_IDR', 'OfferingName', 'SectionName', 
        'Title', 'Credits', 'Department', 'Level', 'Status', 'DOW', 'DOWSort', 'TimeOfDay', 'SubDepartment', 
        'SectionRegRestrictions', 'SeatsAvailable', 'MaxSeats', 'OpenSeats', 'Waitlisted', 'IsWritingIntensive', 
        'AllDepartments', 'Instructors', 'InstructorsFullName', 'Location', 'Building', 'HasBio', 'Areas', 'InstructionMethod', 
        'SectionCoRequisites', 'SectionCoReqNotes', 'SSS_SectionsID', 'Term_JSS', 'Repeatable',

        #SECTION DETAILS, if "SectionDetails" is included, you will write ALL of the below

        'SectionDetails','Description', 'DepartmentID', 'CreditType', 'WebNotes', 'IsCrossListed', 
        'Fees', 'Prerequisites', 'EvaluationUrls', 'PosTags', 'CoRequisites', 'Equivalencies', 'Restrictions', 'Instructors',

        #MEETING DETAILS, if "Meetings" is included, you will write ALL of the below

        'Meetings', 'DOW', 'Dates', 'Times', 'Location', 'Building', 'Room'

    - delim1:
        The delimiter used between selections.
        Used between meetings but not used between meeting selections.

    - delim2:
        The delimiter used between meeting selections.

    - removecharacters:
        Characters

    - fileformat:
    ----------------------------------------------------
    ----------------------------------------------------
    Internally this works by separating the selections into selections that are 

    basic, i.e. just an accessing the dictionary,

    section details i.e. those that go through the step of section details,

    meeting details i.e. those related to meeting times.
    """
    if debug: print(f"Writing to file '{outpath}' with selections: '{selections}'")
    
    #Basic info
    ALLSELECTIONS = np.array(['TermStartDate', 'SchoolName', 'CoursePrefix', 'Term', 'Term_IDR', 'OfferingName', 'SectionName', 
    'Title', 'Credits', 'Department', 'Level', 'Status', 'DOW', 'DOWSort', 'TimeOfDay', 'SubDepartment', 
    'SectionRegRestrictions', 'SeatsAvailable', 'MaxSeats', 'OpenSeats', 'Waitlisted', 'IsWritingIntensive', 
    'AllDepartments', 'Instructors', 'InstructorsFullName', 'Location', 'Building', 'HasBio', 'Areas', 'InstructionMethod', 
    'SectionCoRequisites', 'SectionCoReqNotes', 'SSS_SectionsID', 'Term_JSS', 'Repeatable',
    'SectionDetails', 
    #Section Details
    'Description', 'DepartmentID', 'CreditType', 'WebNotes', 'IsCrossListed', 
    'Fees', 'Prerequisites', 'EvaluationUrls', 'PosTags', 'CoRequisites', 'Equivalencies', #LISTS
    'Restrictions', 'Instructors', #Lists of Dictionaries
    'Meetings', #LIST
    #Meeting details
    'DOW', 'Dates', 'Times', 'Location', 'Building', 'Room'])

    ALLBASICSELECTIONS = ALLSELECTIONS[ : np.where(ALLSELECTIONS == "SectionDetails")[0][0]]
    ALLSECTIONSELECTIONS = ALLSELECTIONS[np.where(ALLSELECTIONS == "SectionDetails")[0][0] : np.where(ALLSELECTIONS == "Meetings")[0][0]]
    ALLMEETINGSELECTIONS = ALLSELECTIONS[np.where(ALLSELECTIONS == "Meetings")[0][0] : ]

    #init
    selection_list = np.array(selections.split(","))
    removecharacters.append(delim1)
    removecharacters.append(delim2)

    #Create groups for each type of selection
    if selections == "all":
        selection_list = ALLSELECTIONS
    else:
        #Check selection_list
        checkkeys = np.isin(selection_list, ALLSELECTIONS)
        if False in checkkeys:
            raise KeyError(f"The following selections are invalid inputs: {selection_list[~checkkeys]}")

    checkkeys_basic = np.isin(selection_list, ALLBASICSELECTIONS)
    basic_selections = selection_list[checkkeys_basic]
    
    if "SectionDetails" in selection_list: #ALL SECTION DETAILS
        section_selections = ALLSECTIONSELECTIONS[1:]
        meetings_selections = ALLMEETINGSELECTIONS[1:]
    elif "Meetings" in selection_list: #ALL MEETINGS
        checkkeys_section = np.isin(selection_list, ALLSECTIONSELECTIONS)
        section_selections = selection_list[checkkeys_section]

        meetings_selections = ALLMEETINGSELECTIONS[1:]
    else: #Just the selected meeting info and section info
        checkkeys_section = np.isin(selection_list, ALLSECTIONSELECTIONS)
        section_selections = selection_list[checkkeys_section]

        checkkeys_meetings = np.isin(selection_list, ALLMEETINGSELECTIONS)
        meetings_selections = selection_list[checkkeys_meetings]
    
    #Options for file format
    with open(outpath,"w") as outfile:
        match fileformat:
            case "delimed":
                if debug: print("delimed")

                #Write header
                if debug: print("Writing header") 
                #Write basic and section selections in the header
                for selection in np.append(basic_selections, section_selections):
                    writestr = f"{selection}"
                    writestr = removeEscapeChr(writestr)
                    for removechr in removecharacters: writestr = writestr.replace(removechr,"")
                    try: outfile.write(writestr + delim1) 
                    except: 
                        if debug: print(f"Error writing '{selection}' to file with class '{courseJson["OfferingName"]}'")
                        outfile.write("ERROR WRITING TO FILE" + delim1) 

                #Write meeting header
                if len(meetings_selections) != 0:
                    outfile.write("MeetingIndex" + delim2) #Meeting index
                    for selection in meetings_selections:
                        outfile.write(selection + delim2)
                    outfile.write(delim1)
                outfile.write("\n")
                #Done writing header


                #Loop through courses and write each one
                for courseJson in fullJson:
                    if debug: print(f"Writing {courseJson["OfferingName"]}")
                    #Basic selections
                    for selection in basic_selections:
                    #IN ALL THE WRITE STATEMENTS, we use replace for loop to remove the delimiters from the string
                        writestr = f"{courseJson[selection]}"
                        writestr = removeEscapeChr(writestr)
                        for removechr in removecharacters: writestr = writestr.replace(removechr,"")
                        try: outfile.write(writestr + delim1)
                        except: 
                            if debug: print(f"Error writing '{selection}' to file with class '{courseJson["OfferingName"]}'")
                            outfile.write("ERROR WRITING TO FILE" + delim1)

                    #Section selections
                    for selection in section_selections:
                        writestr = f"{courseJson["SectionDetails"][0][selection]}"
                        writestr = removeEscapeChr(writestr)
                        for removechr in removecharacters: writestr = writestr.replace(removechr,"")
                        try: outfile.write(writestr + delim1)
                        except: 
                            if debug: print(f"Error writing '{selection}' to file with class '{courseJson["OfferingName"]}'")
                            outfile.write("ERROR WRITING TO FILE" + delim1)
                        
                    #Meeting selections
                    if len(meetings_selections) != 0:
                        writeMeeting(outfile, courseJson, meetings_selections, delim1=delim1, delim2=delim2, removecharacters = removecharacters, debug=debug)


                    #End line
                    outfile.write("\n")


            case "json":
                print("json, not implemented yet") #TODO: IMPLIMENT JSON WRITE MODE

            case _:
                raise KeyError(f"File format given is not possible: {fileformat}")
            
    if debug: print(f"Finished writing to file '{outpath}' with selections: {selection_list}")         

def writeMeeting(outfile, courseJson, selections, delim1 = DELIM1, delim2 = DELIM2, removecharacters = [], debug = DEBUG):
    #Grab meetings
    courseMeetings = courseJson["SectionDetails"][0]["Meetings"]

    #Loop through meetings
    for i,meeting in enumerate(courseMeetings):

        outfile.write("M" + str(i) + delim2) #Meeting index

        #Do all selections
        for selection in selections:
            #Check for special cases
            if selection == "Times" and meeting["Times"] != "": #TIMES special formatting
                times = meeting["Times"].split(" - ")
                #Different time formats
                writestr = f"{times[0]}"
                writestr = removeEscapeChr(writestr)
                for removechr in removecharacters: writestr = writestr.replace(removechr,"")
                outfile.write(writestr + delim2)

                writestr = f"{times[1]}"
                writestr = removeEscapeChr(writestr)
                for removechr in removecharacters: writestr = writestr.replace(removechr,"")
                outfile.write(writestr + delim2)

                
            #No special cases
            else:
                writestr = f"{meeting[selection]}"
                writestr = removeEscapeChr(writestr)
                for removechr in removecharacters: writestr = writestr.replace(removechr,"")
                outfile.write(writestr + delim2)
            

        outfile.write(delim1)

def removeEscapeChr(instr):
    """
    Removes all escape characters
    ---
    Specifically removes these characters that we care about
    
    ["\\n",	
    "\\r",	
    "\\t",	
    "\\b",		
    "\\f",]
    """

    escapeChrs = ["\n",	"\r", "\t", "\b"]

    for character in escapeChrs:
        instr = instr.replace(character, " ")

    return instr
    
def changeKey(keystr):
    """
    Use to change the KEY
    ---
    """
    global KEY
    KEY = keystr

if __name__ == "__main__":
    print("Running examples!")
    #Grabs the data from SIS and stores it in the fullJson variable.
    # This variable is essentially a list of dictionaries with the exact same formatting as SIS outputs.
    fullJson = getFullJson(schools = "WSE,KSAS",term = "/current")
    #The below functions use that data to selectively write certain selections that are of interest for the specific use-case.
    # For example the CoursesRequisites.txt file may be used for a program that shows all the prerequisites for a specific course.
    writeData(fullJson, outpath = "CourseData.txt", selections = "all", debug = False)
    writeData(fullJson, outpath = "BasicCourseData.txt", selections = "Title,OfferingName,SectionName,SchoolName,Term,Instructors,Meetings")
    writeData(fullJson, outpath = "CoursesRequisites.txt", selections = "OfferingName,Prerequisites,CoRequisites,Equivalencies,Restrictions")
    print("done!")