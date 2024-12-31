# SIS-Data-Extractor
 Functions to grab and save data from Johns Hopkins University (JHU) SIS Course Search to a text file for ease of manipulation

 The main purpose of this is to save data from SIS to a text file so that you don't have to constantly do API calls when developing a program or bug testing as the API is quite slow.
 Below is an example of the functions being used to save SIS data into text files.
 ```
 #Grabs the data from SIS and stores it in the fullJson variable.
 # This variable is essentially a list of dictionaries with the exact same formatting as SIS outputs.
 fullJson = getFullJson(schools = "WSE,KSAS",term = "/current")
 #The below functions use that data to selectively write certain selections that are of interest for the specific use-case.
 # For example the CoursesRequisites.txt file may be used for a program that shows all the prerequisites for a specific course.
 writeData(fullJson, outpath = "CourseData.txt", selections = "all", debug = False)
 writeData(fullJson, outpath = "BasicCourseData.txt", selections = "Title,OfferingName,SectionName,SchoolName,Term,Instructors,Meetings")
 writeData(fullJson, outpath = "CoursesRequisites.txt", selections = "OfferingName,Prerequisites,CoRequisites,Equivalencies,Restrictions")
 ```

 If you want to remove the prints done by default on all functions, use the argument debug = False.
 
 Libraries used: numpy, requests