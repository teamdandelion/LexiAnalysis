#!/usr/bin/python
#wordfreq
import sys
import os
args=sys.argv


#compute distance between two texts based on word frequencies. Run from the command line; usage "distance.py filename1 filename2". 

#by Daniel Mane

#The 'text' class manages dictionaries for an individual text. It is never called on by the user; the distComputer class calls it.


def determine_likely_author:
    """Takes a Text, two (or more) TextGroups, and a psuedocount variable. Determines the likely author of the Text, """

def likelihood_comparison(text_dict, group_dict, psuedocount):
    """Generates likelihood that given Text came from given TextGroup. Takes the dictionaries (not the classes) as arguments. Subject to change.
    
    Note that likelihood function has no absolute meaning, since it is a log likelihood with constants disregarded. Instead, the return value may be used as a basis for comparison to decide which TextGroup is more likely to contain the Text. """"
    #Make local copies of the dictionaries so we can alter them without causing problems
    theta_dict = group_dict
    
    numWords = 0
    for word in theta_dict:
        theta_dict[word] += psuedocount
        numWords += theta_dict[word]
    
    for word in text_dict:
        if word not in theta_dict:
            theta_dict[word] = psuedocount
            numWords += psuedocount
    
    theta={}
    
    for word in theta_dict:
        theta[word] = localDict[word] / numWords
    
    loglikelihood = 0
        for word in theta:
            if word in text_dict:
                loglikelihood += testDict[word] * theta[word]
                
    return loglikelihood
    
# class TextGrouping_Excluded(TextGrouping):
#     def __init__(self, textGroup, exclusions)
#         """Builds a dictionary excluding certain Texts form the dictionary
#         
#         Generally used for validation and calibration, i.e. testing the model on known sets of documents. Takes a list of Texts to exclude and generates self.excludedDict and self.excludedWordCount"""
#         self.dict = textGroup.dict
#         self.wordCount = textGroup.wordCount
#         self.
#         for text in exclusions:
#             removalDict = text.dict
#             for word in removalDict:
#                 self.dict[word] -= removalDict[word]
#                 self.wordCount  -= removalDict[word]
#                 if self.excludedDict[word] == 0
#                     del self.excludedDict[word]

class TextGrouping:
    """ A grouping of texts, generally texts by the same author. 
    
    Takes pathName of the directory in which to find the group, and, optionally, a name for the textGroup. Builds a dictionary for all texts in the group (equivalent to concatenation of the texts). Can also build excludedDicts where certain texts are removed for validation and calibration purposes"""
    def __init__(self, pathName, groupName=pathName):
        self.name = groupName
        temp_filenames=os.listdir(pathName)
        self.files=[]
        for file in temp_filenames:
            self.files.append(pathName+"/"+file)
        
        self.documents=[]
        for file in self.files:
            self.documents.append(Text(file))
            
        self.build_combined_dictionary()

    def build_combined_dictionary(self):
        """Builds a combined dictionary of all texts in the TextGroup
        
        Also computes number of words in the dictionary"""
        self.dict={}
        self.wordCount=0
        for document in self.documents:
            self.wordCount += document.wordCount
            
            if self.dict=={}:
                self.dict=document.dict
            else:
                for word in document.dict:
                    if word in self.dict:
                        self.dict[word]+= document.dict[word]
                    else:
                        self.dict[word] = document.dict[word]
    
    def built_excluded_dictionary(self,exclusions):
        """Builds a dictionary excluding certain Texts form the dictionary
        
        Generally used for validation and calibration, i.e. testing the model on known sets of documents. Takes a list of Texts to exclude and generates self.excludedDict and self.excludedWordCount"""
        self.excludedDict = self.dict
        self.excludedWordCount
        for text in exclusions:
            removalDict = text.dict
            for word in removalDict:
                self.excludedDict[word] -= removalDict[word]
                self.excludedWordCount  -= removalDict[word]
                if self.excludedDict[word] == 0
                    del self.excludedDict[word]
        
    
    def report(self):
        for word in self.dict:
            print(word, self.dict[word])
        print "Word count was: ", self.wordCount
            
            

class Text:
    """Manages dictionary for a single text."""
#The initialization calls on all methods needed to populate the class
    def __init__(self, fileName):
        file=open(fileName, 'r')
        self.contents=file.read().split()
        self.wordCount = len(self.contents)
        #Splits the contents into words - note punctuation needs to be taken care of later
        self.buildDict() 
        #Builds the dictionary, creating self.wordCount, self.Dict
           
    def buildDict(self):
        self.dict={}
        for word in self.contents:
            wx=word.strip('?.()[]-:!;,"\'').lower()
            if wx in self.dict:
                self.dict[wx]+=1
            else:
                self.dict[wx]=1
                
#TextGrouping(args[1])