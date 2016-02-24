#!/usr/bin/env python

"""dprimer.py: A script to compute d' from the Alpha Detector in OpenVibe. """

from __future__ import division # Not neccessary in Python 3 and later
from scipy.stats import norm
from math import exp,sqrt
import csv
import pandas as pd


# NOTE: the d prime calculation is respectfully taken from Jonas Lindelov's 
#great tutorial on calculating D', Beta, C, and AD' in python and PHP. The #tutorial is available at http://lindeloev.net/?p=29

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

################################################################################
''' Now to get to using the csv files created by OpenVibe! '''

#This section uses the pandas module to manipulate the data

df = pd.read_csv('record-2016.02.22-11.34.46.csv', sep=';', header=0)
keep_cols = ["Identifier"]
df = df[keep_cols]
df.to_csv("data.csv", index=False)

def stim(row):
    if row['Identifier'] == stim_alpha:
        return 1
    elif row['Identifier'] == stim_nonalpha:
        return 5

def detect(row):
    if row['Identifier'] == detect_alpha:
        return 10
    elif row['Identifier'] == detect_nonalpha:
        return 20
    
def classifier(row):
    return row['Stim']+row['Detect']

df['Stim']   = df.apply(stim,axis=1)
df['Detect'] = df.apply(detect,axis=1)
df['Classifier'] = df.apply(classifier,axis=1)

print df

'''
for row in df:
	if stim_alpha:
		stim = 1
		print "eyes closed"
	elif stim_nonalpha:
		stim = 0
		print "eyes open"

for row in df:
	if detect_alpha:
		detect = 1
		print "alpha detected"
	elif detect_nonalpha:
		detect = 0
		print "alpha not detected!"

print stim
print detect
'''





'''
df1 = df.pivot_table(index='Identifier',values='Time (s)',aggfunc=len)

#df_predict_alpha = df[df['Identifier'] == predict_alpha]

print df_predict_alpha.head(5)

'''
#This section uses the csv module to manipulate the data.
'''
f = open('record-2016.02.22-11.34.46.csv') # Opes up the file written by OV

with f as source:
	rdr= csv.reader(f, delimiter=';')
	with open("result", "wb") as result:
		wtr= csv.writer( result )
		for r in rdr:
			wtr.writerow( (r[1]) )
			
print wtr

for row in csv.f:
	if predict_alpha == row[1]:
		# 1)get the corresponding timestamp for each iteration of predict_alpha.
			# 2) look to see what the most recent stim_x is, for every iteration of predict_alpha.
				#then make a count of how many times stim_alpha is the most 	
				#recent stim_x. Place this count in the variable "hits"
				#now make a count of how many times stim_nonalpha is the most 	
				#recent stim_x. Place this count in the variable "misses."
		print "is there!"
	if predict_nonalpha == row[1]:
		#get the corresponding timestamp for each iteration of predict_nonalpha.
			#code that looks looks to see what the most recent stim_x is, for 
			#every iteration of predict_nonalpha.
				#then make a count of how many times stim_alpha is the most 	
				#recent stim_x. Place this count in the variable "fas."
				#now make a count of how many times stim_nonalpha is the most 	
				#recent stim_x. Place this count in the variable "crs."
		print "is there2"

file.close

'''

################################################################################
""" Now, on to computing d'! """

hits = 20
misses = 5
fas = 10
crs = 15

Z = norm.ppf

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
    out['beta'] = exp(Z(faRate)**2 - Z(hitRate)**2)/2
    out['c'] = -(Z(hitRate) + Z(faRate))/2
    out['Ad'] = norm.cdf(out['d']/sqrt(2))
    return out
    
d = dPrime(hits,misses,fas,crs)
print d