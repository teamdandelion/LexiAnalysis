#!/usr/bin/python
#wordfreq
import sys
import os
import math
import copy
import pdb
 
from texts import Text, TextGroup, TextGroup_Excluded

args = sys.argv

DEFAULT_MIN = .02
DEFAULT_STEP = .02
DEFAULT_N_STEPS = 100

class ClassificationManager:
    """Manages a group of documents and classifications from start to finish.
    
    Takes a name of directory containing classified training examples 
    (organized by folder: see below), and name of a directory containing 
    unknown unclassified examples. Will expand directory tree of classified 
    examples and expects to find subdirectories with the group names, e.g.:
    /Known/
        .../Hamilton    <- contains documents known to be written by Hamilton
        .../Madison     <- contains documents known to be written by Madison
    /Unknown/  <- contains documents in need of classification
    
    Method 'validate' will validate and calibrate using the training examples; 
    based on user input, it can try a lot of psuedocount values and report 
    which worked best, and the user can specify psuedocount values to test
    
    Method 'classify' will classify the unknown documents given a user-
    specified psuedocount
    
    """
    def __init__(self,known_dir="Known", unknown_dir="Unknown"):
        self.known_Text_Groups = []
        
        if not os.path.isdir(known_dir) or not os.path.isdir(unknown_dir):
            print """Error: Unable to find known directory './known/' or unknown directory './unknown/'. 
            Please seed README for usage details."""
            exit(-1)
        
        for entry in os.listdir(known_dir):
            path_name = known_dir + "/" + entry
            if os.path.isdir(path_name):
                #pdb.set_trace()################################################
                "Presently making a known TextGroup from a known directory"
                new_text_group = TextGroup(path_name, entry)
                self.known_Text_Groups.append(new_text_group)
        
        self.unknown_Texts = []
        for entry in os.listdir(unknown_dir):
            file_name = unknown_dir + "/" + entry
            if file_name.endswith(".txt"):
                self.unknown_Texts.append(Text(file_name))
        
        n_known_TG = len(self.known_Text_Groups)
        n_known_documents = 0
        for tg in self.known_Text_Groups:
            n_known_documents += len(tg.documents)
        n_unknown = len(self.unknown_Texts)
        
        print "Files loaded properly. Found {1} known documents in {0} groups; {2} unknown documents".format(n_known_TG, n_known_documents, n_unknown)
                
    def calibration(self,psuedo_min=DEFAULT_MIN, psuedo_step=DEFAULT_STEP, 
                                                n_steps=DEFAULT_N_STEPS):
        print("Initiating validation procedure. \n"+
                "Results are automatically saved to ./validation.txt. \n"+
                "Each run of validation overwrites previous results, so "+
                "save them if you want to hold onto them.")
        print #Throw another newline for clarity
        psuedo_sequence = arithmetic_progression(psuedo_min, psuedo_step,
                                                                    n_steps)
        outputFile = open('validation.txt','w')
        print "Psuedocount  #Mistakes  Average Difference"
        outputFile.write("Psuedocount  #Mistakes  Average Difference\n")
        for psuedocount in psuedo_sequence:
            mistakes=0
            documents_seen=0
            total_diff=0
            
            for group in self.known_Text_Groups:
                other_groups = copy.copy(self.known_Text_Groups)
                # Only shallow copy needed because we change the set of text
                # groups, but do *not* modify the text groups themselves.
                other_groups.remove(group)
                # Generate list of groups to compare against. Remove the current 
                # group so we can add an exclusion group later, i.e. group 
                # with the validation document removed. This ensures that 
                # the document we are validating is not included in the 
                # training set
                for document in group.documents:
                    documents_seen+=1
                    exclusion_group = TextGroup_Excluded(group,document)
                    comparison_group = copy.copy(other_groups)
                    # We are adding another text group, so we need another
                    # shallow copy. 
                    comparison_group.append(exclusion_group)
                    classification = classify(document, comparison_group, 
                                                psuedocount)
                    if classification[0] == exclusion_group:
                        # We got the right classification
                        total_diff += classification[1]
                    else:
                        mistakes += 1
                        total_diff -= classification[1]

            mistake_rate = float(mistakes) / documents_seen
            average_diff = float(total_diff) / documents_seen
            resultsString = "{0:3.2f}         {2:3.0f}            {3:5.0f}".format(psuedocount, documents_seen, mistakes, average_diff)
            print resultsString
            outputFile.write(resultsString + "\n")
                
    def classify_unknown(self,psuedocount=.5):
        print("Initiating classification procedure. \n "+
                "Will report classifications and save to 'classification.txt'")
        outFile = open("classification.txt","w")
        print "Psuedocount = {0}".format(psuedocount)
        outFile.write("Psuedocount = {0}\n".format(psuedocount))
        print "Classification     Difference"
        outFile.write("Classification      Difference\n")
        
        for doc in self.unknown_Texts:
            cfc = classify(doc, self.known_Text_Groups, psuedocount)
            out_string = ("{0:15s}                         ".format(cfc[0].name)+
                    "{0:5.0f}".format(cfc[1]))
            print out_string
            outFile.write(out_string + "\n")          


def classify(text, groups, psuedocount):
    """Classifies a text into one of the provided groups, given a psuedocount.
    
    Returns a tuple containing the chosen group and the difference in log-
    likelihood between the chosen group and the second best option 
    (for validation purposes and perhaps confidence estimation).
    
    """
    comparisons = {}
    for group in groups:
        comparisons[group] = likelihood_comparison(text, group, psuedocount)
        #print text.name
        #print "{0:12s} {1:5.0f}".format(group.name, comparisons[group])
    
    max  = float("-inf")
    second_max = float("-inf")

    
    for group in comparisons:
        if comparisons[group] > second_max:
            if comparisons[group] > max:
                second_max = max
                max = comparisons[group]
                classification = group
            else:
                second_max = comparisons[group]
    
    diff = max - second_max
    assert diff > 0
    return (classification, diff)
        
        
        
        
        
        
        
        
        
        

def likelihood_comparison(text, group, psuedocount):
    """Generates log-likelihood that given Text came from given TextGroup.
    
    Note that likelihood function has no absolute meaning, since it is a log-
    likelihood with constants disregarded. Instead, the return value may be 
    used as a basis for comparison to decide which TextGroup is more likely to 
    contain the Text. 
    
    """
    #Make local copies of the dictionaries so we can alter them without causing 
    #problems
    theta_dict = copy.copy(group.dict)
    
    numWords = float(0)
    assert len(theta_dict)!= 0
    for word in theta_dict:
        theta_dict[word] += psuedocount
        numWords += theta_dict[word]
    
    for word in text.dict:
        if word not in theta_dict:
            theta_dict[word] = psuedocount
            numWords += psuedocount
    
    theta = {}
    
    for word in theta_dict:
        theta[word] = theta_dict[word] / numWords
        if theta[word] == 0:
            print "Tenemos un problema: {0}, {1}".format(theta_dict[word],numWords)
            assert(1+1==3)
    
    loglikelihood = 0
    if len(text.dict)==0:
        print "Woahh!!!"
    for word in text.dict:
        #if text.name == "madison1.txt":
            #print "Word: {0:5s} TextCount: {1:3f} GrouptCount {2:3f}".format(word, text.dict[word], theta_dict[word])
        loglikelihood += text.dict[word] * math.log(theta[word])
        if text.dict[word] * math.log(theta[word]) == 0:
            print text.dict[word], math.log(theta[word])
            assert(1+1==3)
                
    return loglikelihood
    


def arithmetic_progression(start, step, length):
    for i in xrange(length):
        yield start + i * step
        
        
def user_interaction():
    choice = raw_input("Would you like to run validation or "+
                            "start classifying or quit? (v/c/q)?")
    while (choice != 'v' and choice != 'c' and choice != 'q'):
        choice = input("Please choose (v)alidation or "+
                                        "(c)classifying or (q)uit")
    
    if choice == 'q':
        exit(0)
    
    if choice == "v":
        default = "x"
        while default != "y" and default != "n":
            default = raw_input("Would you like to run validation with the "+
                    "defaults \n Min {0}, Step {1}, # steps {2}".format(
                                DEFAULT_MIN, DEFAULT_STEP, DEFAULT_N_STEPS) +
                    " (y/n)?")
        if default == "y":
            manager.validation()
    
        else:
            p_min    = float(raw_input("Input the miniumum psuedocount:"))
            p_step   = float(raw_input("Input the psuedocount step size:"))
            p_nsteps = int(  raw_input("Input the number of steps:"))
            print
            manager.validation(p_min,p_step,p_nsteps)
        user_interaction()

    if choice == "c":
        p_count = float(raw_input("Input the psuedocount to use:"))
        manager.classify_unknown(p_count)
    


print #Make things a bit more clean by printing a newline
manager = ClassificationManager()
user_interaction()

