#!/usr/bin/python
#wordfreq
import sys
import os
import math
import copy
import pdb
 
from texts import Text, TextGroup, TextGroup_Excluded

args = sys.argv



class ClassificationManager:
    """Manages a group of documents and classifications from start to finish.
    
    Takes a name of directory containing classified training examples 
    (organized by folder: see below), and name of a directory containing 
    unknown unclassified examples. Will expand directory tree of classified 
    examples and expects to find subdirectories with the group names, e.g.:
    /Known_Examples/
        .../Hamilton    <- contains documents known to be written by Hamilton
        .../Madison     <- contains documents known to be written by Madison
    /Unknown_Examples/  <- contains documents in need of classification
    
    Method 'validate' will validate and calibrate using the training examples; 
    based on user input, it can try a lot of psuedocount values and report 
    which worked best, and the user can specify psuedocount values to test
    
    Method 'classify' will classify the unknown documents given a user-
    specified psuedocount
    
    """
    def __init__(self,known_dir, unknown_dir):
        self.known_Text_Groups = []
        
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
                
    def validation(self,psuedo_min=.01,psuedo_step=.01,n_steps=200):
        #pdb.set_trace()
        "Initiating validation procedure"
        psuedo_sequence = arithmetic_progression(psuedo_min, psuedo_step,
                                                                    n_steps)
        
        print "Psuedocount  #Mistakes  Average Difference"
        for psuedocount in psuedo_sequence:
            #pdb.set_trace()
            "Trying a new psuedocount"
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
                    #pdb.set_trace()
                    "testing a document"
                    documents_seen+=1
                    exclusion_group = TextGroup_Excluded(group,document)
                    comparison_group = copy.copy(other_groups)
                    # We are adding another text group, so we need another
                    # shallow copy. 
                    comparison_group.append(exclusion_group)
                    #pdb.set_trace()
                    "classifying"
                    classification = classify(document, comparison_group, 
                                                psuedocount)
                    if classification[0] == exclusion_group:
                        # We got the right classification
                        #print "{0} was classified correctly, diff {1:5.2f}".format(document.name, classification[1])
                        total_diff += classification[1]
                    else:
                        mistakes += 1
                        total_diff -= classification[1]
                        #print "{0} was classified incorrectly, diff {1:5.2f}".format(document.name, classification[1])
            mistake_rate = float(mistakes) / documents_seen
            average_diff = float(total_diff) / documents_seen
            print "{0:3.2f}         {2:3.0f}            {3:5.0f}".format(psuedocount, documents_seen, mistakes, average_diff)
                










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



manager=ClassificationManager("Known","Unknown")
manager.validation(float(args[1]),float(args[2]),int(args[3]))