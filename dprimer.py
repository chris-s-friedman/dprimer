#!/usr/bin/env python

"""dprimer.py: A script to compute d' from the Alpha Detector in OpenVibe. """

from __future__ import division # Not neccessary in Python 3 and later
from scipy.stats import norm
from math import exp,sqrt
from numpy import isnan
import csv
import pandas as pd


# NOTE: the d prime calculation is taken from Jonas Lindelov's great tutorial on
#calculating D', Beta, C, and AD' in python and PHP. The #tutorial is available 
#at http://lindeloev.net/?p=29

################################################################################
''' Naming the variables that come out of OpenVibe'''

# First, we name our variables. These correspond to stimulation labels, as saved
# by the CSV file writer in OV. 

# These two are the two stimuli presented to subjects. The first prompts subject
# to be in a state non-conducive to alpha production; the second prompts subject 
# to be in a state conducive to alpha production (e.g. for occipital alpha, eyes
# open and eyes closed, respectively). 
stim_alpha = 33031 #OVTK_StimulationId_Label_01 
stim_nonalpha = 33025 #OVTK_StimulationId_Label_07

# These two are the predictions made by openvibe, regarding the derivative of
# the alpha bump. 
detect_alpha = 33285 #OVTK_StimulationId_Target 
detect_nonalpha = 33286 #OVTK_StimulationId_NonTarget 

# These four are the four possible classifications for each detection
class_hit = stim_alpha + detect_alpha
class_miss = stim_alpha + detect_nonalpha
class_fa = stim_nonalpha + detect_alpha
class_cr = stim_nonalpha + detect_nonalpha

################################################################################
''' Now to get to using the csv files created by OpenVibe! '''

# Import the stimulation and threshold file

df_stim = pd.read_csv('stim.csv', sep=';', header=0) # Load up stimulations
keep_cols = ["Time (s)", "Identifier"] #define the columns we want in stims
df_stim = df_stim[keep_cols] # Remove unwanted "duration column
df_thresh = pd.read_csv('thresh.csv', sep=';', header=0) #load up the thresholds

df = df_stim.merge(df_thresh, left_on='Time (s)', right_on='Time (s)',
	how='outer') # Merge the stim and threshold files
df = df.sort('Time (s)') # Orders the data frame by time

#This section uses the pandas module to manipulate the data

df = pd.read_csv('record-2016.02.22-11.34.46.csv', sep=';', header=0) #read data
keep_cols = ["Time (s)", "Identifier"] 
df = df[keep_cols] # Removes unwanted columns (time and length of stim)

# adds the "Stim" column, telling us what our stim is. 
df.loc[df['Identifier'] == stim_alpha, 'Stim'] = stim_alpha
df.loc[df['Identifier'] == stim_nonalpha, 'Stim'] = stim_nonalpha

# adds the "detect column, telling us what the detection is.
df.loc[df['Identifier'] == detect_alpha, 'Detect'] = detect_alpha
df.loc[df['Identifier'] == detect_nonalpha, 'Detect'] = detect_nonalpha

#fill NaN by method ffill (propagate last valid observation forward to next 
#valid). This makes it so every detection is connected to some stim. 
df['Stim'] = df['Stim'].ffill()

#creates a classifier column
df['Classifier'] = df['Stim'] + df['Detect']

df.loc[isnan(df['Classifier']) == False, 'Start'] = df['Time (s)']
#df.loc[isnan(df['Classifier']) == False, 'End'] = 

#using the classifier, detects if each instance is a hit, miss, etc. 
hits = df[df['Classifier']== class_hit].count()["Classifier"]
misses = df[df['Classifier']== class_miss].count()["Classifier"]
fas = df[df['Classifier']== class_fa].count()["Classifier"]
crs = df[df['Classifier']== class_cr].count()["Classifier"]

#print out the value of each type to the console. 
print "hits:", hits
print "misses:", misses
print "False Alarms:", fas
print "Correct Rejections:", crs


################################################################################
""" Now, on to computing d'! """

#computes z
Z = norm.ppf


#d' calculator
def dPrime(hits, misses, fas, crs):
    # Floors and ceilings are replaced by half hits and half FA's
    halfHit = 0.5/(hits+misses)
    halfFa = 0.5/(fas+crs)
 
    # Calculate hitrate and avoid d' infinity
    hitRate = hits/(hits+misses)
    if hitRate == 1: hitRate = 1-halfHit
    if hitRate == 0: hitRate = halfHit
 
    # Calculate false alarm rate and avoid d' infinity
    faRate = fas/(fas+crs)
    if faRate == 1: faRate = 1-halfFa
    if faRate == 0: faRate = halfFa
 
    # Return d', beta, c and Ad'
    out = {}
    out['d'] = Z(hitRate) - Z(faRate)
    #out['beta'] = exp(Z(faRate)**2 - Z(hitRate)**2)/2
    #out['c'] = -(Z(hitRate) + Z(faRate))/2
    #out['Ad'] = norm.cdf(out['d']/sqrt(2))
    return out
    
d = dPrime(hits,misses,fas,crs)

#prints d' to the console.
print d