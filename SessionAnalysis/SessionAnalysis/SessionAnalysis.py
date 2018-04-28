# Using Python 3.6

import os, io, re
from datetime import datetime
from datetime import timedelta
from functools import reduce

path = 'E:\\Users\\timregan\\Microsoft\\ProjectTorino - Documents\\Logs from Trialists\\'
csvFileLines = [ 'Name,DateTime,Duration,PlayCount,ReadCount' ]
maxSecondsGapInSession = 3600 # One hour

def GetSession(name):
    return { 'name' : name, 'start' : '', 'duration' : 0, 'offset' : 0, 'numPlay' : 0, 'numRead' : 0 }

def AddSessionToCSV(session, csvLines):
    if session['start'] != '' and session['duration'] != '':
        try:
            start = datetime.strptime(session['start'], '%d/%m/%Y %H:%M:%S')
        except ValueError:
            start = datetime.strptime(session['start'], '%m/%d/%Y %I:%M:%S %p')
        if start:
            start = start + timedelta(seconds=session['offset'])
            startStr = datetime.strftime(start, '%d/%m/%Y %H:%M:%S')
        else:
            startStr = session['start']
        csvLines.append(session['name'] + ',' + startStr + ',' + str(session['duration'] - session['offset']) + ',' + str(session['numPlay']) + ',' + str(session['numRead']))

# Read the sub directories
blah = next(os.walk(path))
subDirs = blah[1]

# Read and process the logs in each sub-directory
for subDir in subDirs:

    # Read the log, code, and exception files so that we can ingest them
    loggedFileNames = [fileName for fileName in os.listdir(path + subDir + '\\Logs') if fileName.lower().endswith('txt')]

    # Run through the log files
    for logFileName in [fileName for fileName in loggedFileNames if fileName.lower().startswith('log')]:

        # Set up counts etc.
        currentSession = GetSession(subDir)
        previousDuration = 0

        # Open the log file
        with io.open(path + subDir + '\\Logs\\' + logFileName, 'r', encoding='latin-1') as file:

            # Read the log file and split it into lines
            fileTextLines = file.read().split('\n')

            if len(fileTextLines) > 0 and fileTextLines[0].startswith('Log started: '):

                # Process each line
                for fileTextLine in fileTextLines:

                    # Parse out the duration
                    match = re.search('\] \[([0-9]+)', fileTextLine)
                    if match != None:
                        candidateDuration = match.group(1)
                        if candidateDuration != '':
                            durationInt = int(candidateDuration)
                            if (durationInt - previousDuration) > maxSecondsGapInSession:
                                # We need to start a new session
                                AddSessionToCSV(currentSession, csvFileLines)
                                newSession = GetSession(subDir)
                                newSession['start'] = currentSession['start']
                                newSession['offset'] = durationInt
                                currentSession = newSession
                            else:
                                currentSession['duration'] = durationInt
                            previousDuration = durationInt

                    # Save the date and time
                    if fileTextLine.startswith('Log started: '):
                        currentSession['start'] = fileTextLine.replace('Log started: ', '')

                    # Increment the counts
                    if 'StartPlaying' in fileTextLine:
                        currentSession['numPlay'] = currentSession['numPlay'] + 1
                    if 'ReadCode' in fileTextLine:
                        currentSession['numRead'] = currentSession['numRead'] + 1


                    # TODO: Load the coad file and keep maxumum number of nodes and list of node types
                    
        AddSessionToCSV(currentSession, csvFileLines)

# Save the CSV to disk
with io.open(path + '\\Sessions.csv', 'w') as outputFile:
    mergedOutputLines = '\n'.join(csvFileLines)
    outputFile.writelines(mergedOutputLines)