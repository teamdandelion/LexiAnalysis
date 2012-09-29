#!/usr/bin/python
#wordfreq
import sys
import os
import math
import copy
import pdb
 
from texts import Text, TextGroup, TextGroup_Excluded

args = sys.argv

DEFAULT_MIN     = .1
DEFAULT_STEP    = .1
DEFAULT_N_STEPS = 20

KNOWN_DIRECTORY = "Known"
UNKNOWN_DIRECTORY = "Unknown"

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
    def __init__(self,known_dir=KNOWN_DIRECTORY, unknown_dir=UNKNOWN_DIRECTORY):
        self.known_Text_Groups = []
        
        if not os.path.isdir(known_dir) or not os.path.isdir(unknown_dir):
            print("Error: Unable to find known directory " + known_dir + 
                    "or unknown directory " + unknown_dir + "\n" +
                    "Please see README for usage details.")
            exit(-1)
        
        for entry in os.listdir(known_dir):
            path_name = known_dir + "/" + entry
            if os.path.isdir(path_name):
                "Presently making a known TextGroup from a known directory"
                self.known_Text_Groups.append(TextGroup(path_name, entry))
        
        self.unknown_Texts = []
        for entry in os.listdir(unknown_dir):
            file_name = unknown_dir + "/" + entry
            if file_name.endswith(".txt"):
                self.unknown_Texts.append(Text(file_name, entry))
        
        self.n_known_TG = len(self.known_Text_Groups)
        self.n_known_documents = 0
        for tg in self.known_Text_Groups:
            self.n_known_documents += len(tg.documents)
        self.n_unknown = len(self.unknown_Texts)
        
        print("Files loaded properly. \n"
                "Found {1} known documents in {0} " 
                "groups; {2} unknown documents".format(self.n_known_TG,
                self.n_known_documents, self.n_unknown))
                
    def calibrate(self,psuedo_min=DEFAULT_MIN, psuedo_step=DEFAULT_STEP, 
                                                n_steps=DEFAULT_N_STEPS):
        print("Initiating validation procedure. \n"
                "Results are automatically saved to calibration.txt. \n"
                "Each run of validation overwrites previous results.")
        print #Throw another newline for clarity
        psuedo_sequence = arithmetic_progression(psuedo_min, psuedo_step,
                                                                 n_steps)
        outputFile = open('calibration.txt','w')
        print "Psuedocount  #Mistakes  Average Difference"
        outputFile.write("Psuedocount  #Mistakes  Average Difference\n")
        for psuedocount in psuedo_sequence:
            mistakes=0
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

            average_diff = float(total_diff) / self.n_known_documents
            results_str = ("{0:3.2f}".format(psuedocount).ljust(15) + 
                           "{0:3.0f}".format(mistakes).ljust(12) +
                           "{0:5.0f}".format(average_diff))
            print results_str
            outputFile.write(results_str + "\n")
        
    def validate(self,psuedocount):
        print("Initiating validation procedure. \n Will report "
                "classifications of known documents and save to "
                "'validation.txt'")
        out_file=open("validation.txt","w")
    
        header = ("Document:  ".ljust(14) + "     Classification:  " + 
                    "LLV:  " + "    Diff:")
        print(header)
        out_file.write(header + "\n")
        
        for group in self.known_Text_Groups:
            other_groups = copy.copy(self.known_Text_Groups)
            other_groups.remove(group)
            for document in group.documents:
                exclusion_group = TextGroup_Excluded(group,document)
                comparison_group = copy.copy(other_groups)
                # We are adding another text group, so we need another
                # shallow copy. 
                comparison_group.append(exclusion_group)
                classification = classify(document, comparison_group, 
                                            psuedocount)
                if classification[0] == exclusion_group:
                    out_string= ("{0:18s} {1:8s} {2:13.0f} {3:9.0f}".format(
                        document.name, classification[0].name[:-3], 
                        classification[2], classification[1]))
                    print(out_string)
                    out_file.write(out_string + "\n")
                else:
                    out_string=("{0:18s} {1:8s} {2:13.0f} {3:9.0f}".format(
                        document.name, classification[0].name, 
                        classification[2], -1*classification[1]))
                    print(out_string)
                    out_file.write(out_string + "\n")
                        
    def classify_unknown(self,psuedocount=.5):
        print("Initiating classification procedure. \n "+
                "Will report classifications and save to 'classification.txt'")
        out_file = open("classification.txt","w")
        print "Psuedocount = {0}".format(psuedocount)
        print
        out_file.write("Psuedocount = {0}\n".format(psuedocount))
        header = ("Document:".ljust(14) + "Classification:".ljust(20) 
                    + "LLV:".ljust(15) + "Difference:")
        print header
        out_file.write(header+"\n")
        
        for doc in self.unknown_Texts:
            cfc = classify(doc, self.known_Text_Groups, psuedocount)
            out_string = ("{0:14s} {1:18s}".format(doc.name, cfc[0].name) +         
                    "{0:7.0f}".format(cfc[2]) + "{0:14.0f}".format(cfc[1]))
                #cfc = ClassiFiCation, i just wanted a short variable name
            print out_string
            out_file.write(out_string + "\n")        
        out_file.close()  


def classify(text, groups, psuedocount):
    """Classifies a text into one of the provided groups, given a psuedocount.
    
    Returns a tuple containing the chosen group and the difference in log-
    likelihood between the chosen group and the second best option 
    (for validation purposes and perhaps confidence estimation).
    
    """
    comparisons = {}
    for group in groups:
        comparisons[group] = likelihood_comparison(text, group, psuedocount)    
    max  = float("-inf")
    second_max = float("-inf")
    
    #Want to find the maximum LLV (to classify the group) and the second-maximum
    #LLV (to report the difference)
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
    return (classification, diff, max)
        
        
def likelihood_comparison(text, group, psuedocount):
    """Generates log-likelihood that given Text came from given TextGroup.
    
    Note that likelihood function has no absolute meaning, since it is a log-
    likelihood with constants disregarded. Instead, the return value may be 
    used as a basis for comparison to decide which TextGroup is more likely to 
    contain the Text. 
    
    """
    #Make local copies of the dictionaries so we can alter them without causing problems
    theta_dict = copy.copy(group.dict)
    
    numWords = float(0)
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

    loglikelihood = 0
    for word in text.dict:
        loglikelihood += text.dict[word] * math.log(theta[word])                
    return loglikelihood

def arithmetic_progression(start, step, length):
    for i in xrange(length):
        yield start + i * step
        #Got this code from stackoverflow

def user_interaction():
    choice = raw_input("Would you like to run cali(b)ration or \n"
                        "(v)alidation or (c)lassification or "
                        "(q)uit? (b/v/c/q)")
                        
    while (choice != 'v' and choice != 'c' and choice != 'q' and choice != 'b'):
        choice = raw_input("Please choose cali(b)ration or (v)alidation or "+
                                        "(c)lassification or (q)uit")
    if choice == 'q':
        exit(0)
        
    if choice == "b":
        default = "x"
        while default != "y" and default != "n":
            default = raw_input("Would you like to run calibration with the "+
                    "defaults \n Min {0}, Step {1}, # steps {2}".format(
                                DEFAULT_MIN, DEFAULT_STEP, DEFAULT_N_STEPS) +
                    " (y/n)?")
        if default == "y":
            manager.calibrate()
        else:
            p_min    = float(raw_input("Input the miniumum psuedocount:"))
            p_step   = float(raw_input("Input the psuedocount step size:"))
            p_nsteps = int(  raw_input("Input the number of steps:"))
            print
            manager.calibrate(p_min,p_step,p_nsteps)

    if choice == "c":
        p_count = float(raw_input("Input the psuedocount to use:"))
        manager.classify_unknown(p_count)
    
    if choice == "v":
        p_count = float(raw_input("Input the psuedocount to use:"))
        manager.validate(p_count)
    
print #Make things a bit more clean by printing a newline
manager = ClassificationManager()
while(1): #Program will exit when user chooses to quit
    user_interaction()

