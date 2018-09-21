# Using Python 3.6

import os, io, re
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
from functools import reduce

# Constants
path = 'E:\\Users\\timregan\\Microsoft\\ProjectTorino - Documents\\Logs from Trialists\\'
maxSecondsGapInSession = 3600 # One hour

# Returns an 'empty' session
def GetSession(name, file):
    return { 
        'name' : name, 
        'logFile' : file, 
        'start' : '', 
        'duration' : 0, 
        'offset' : 0, 
        'numPlay' : 0, 
        'numRead' : 0,
        'minNodeCount' : 1, 
        'minThreadCount' : 1, 
        'maxNodeCount' : 0, 
        'maxThreadCount' : 0, 
        'singleThreadedSequences' : False, 
        'multiThreadedSequences' : False, 
        'loopNowtBeforeOrAfter' : False, 
        'followedLoops' : False, 
        'loopsOnMultipleThreads' : False, 
        'constantsNoVariables' : False, 
        'randomOrInfinityNoVariables' : False, 
        'manualSelection' : False, 
        'selectionInLoop' : False, 
        'independentCounters' : False, 
        'variablesWithoutCounters' : False, 
        'countersWithVariables' : False, 
        'nestedLoops' : False } 

# Add the given session as a line to the list of CSV file lines
def AddSessionsToCSV(sessions, csvLines):
    for session in sessions:
        # Only act on sessions with stuff in
        if session['start'] != '' and session['duration'] != '' and (session['numPlay'] != 0 or session['numRead'] != 0):
            # Sadly there are two DateTime formats in use in the log files, we should not have left that as a local choice
            try:
                start = datetime.strptime(session['start'], '%d/%m/%Y %H:%M:%S')
            except ValueError:
                start = datetime.strptime(session['start'], '%m/%d/%Y %I:%M:%S %p')
            if start:
                # Add the offset, say to the first play, to the start time
                start = start + timedelta(seconds=session['offset'])
                startStr = datetime.strftime(start, '%d/%m/%Y %H:%M:%S')
            else:
                startStr = session['start']
            # Add the resulting data
            csvLines.append(
                session['name'] + ',' + 
                session['logFile'] + ',' + 
                startStr + ',' + 
                str(session['duration'] - session['offset']) + ',' + 
                str(session['numPlay']) + ',' + 
                str(session['numRead']) + ',' + 
                str(session['minNodeCount']) + ',' + 
                str(session['minThreadCount']) + ',' + 
                str(session['maxNodeCount']) + ',' + 
                str(session['maxThreadCount']) + ',' + 
                str(session['singleThreadedSequences']) + ',' + 
                str(session['multiThreadedSequences']) + ',' + 
                str(session['loopNowtBeforeOrAfter']) + ',' + 
                str(session['followedLoops']) + ',' + 
                str(session['loopsOnMultipleThreads']) + ',' + 
                str(session['constantsNoVariables']) + ',' + 
                str(session['randomOrInfinityNoVariables']) + ',' + 
                str(session['manualSelection']) + ',' + 
                str(session['selectionInLoop']) + ',' + 
                str(session['independentCounters']) + ',' + 
                str(session['variablesWithoutCounters']) + ',' + 
                str(session['countersWithVariables']) + ',' + 
                str(session['nestedLoops']))


# Run through the code file to gather Alex's metrics
def ParseCodeFile(lines):
    code = { 
        'nodeCount' : 0, 
        'threadCount' : 0, 
        'singleThreadedSequences' : False, 
        'multiThreadedSequences' : False, 
        'loopNowtBeforeOrAfter' : False, 
        'followedLoops' : False, 
        'loopsOnMultipleThreads' : False, 
        'constantsNoVariables' : False, 
        'randomOrInfinityNoVariables' : False, 
        'manualSelection' : False, 
        'selectionInLoop' : False, 
        'independentCounters' : False, 
        'variablesWithoutCounters' : False, 
        'countersWithVariables' : False, 
        'nestedLoops' : False } 
    inLoop = 0
    loopCount = 0
    loopInThreadCounts = {}
    inLoopWithNowtBefore = False
    selectionCount = 0
    playCount = 0
    pauseCount = 0

    # Process each line
    for index, line in enumerate(lines):

        if line.startswith('Thread'):
            # Increment thread count
            code['threadCount'] = code['threadCount'] + 1

            # Set up (or inrement) dictionary that counts number of loops on each thread
            if len(loopInThreadCounts.keys()) == 0:
                loopInThreadCounts[0] = 0
            else:
                loopInThreadCounts[max(loopInThreadCounts.keys()) + 1] = 0

        elif line.startswith('Play'):
            playCount = playCount + 1

        elif line.startswith('Pause'):
            pauseCount = pauseCount + 1

        elif line.startswith('If'):
            # Increment selection count
            selectionCount = selectionCount + 1

            # Check if this selection is in a loop
            if inLoop > 0:
                code['selectionInLoop'] = True

            # Check for manual selection
            match = re.search('If [1-8] is greater than [1-8]', line)
            if match != None:
                code['manualSelection'] = True

        elif line.startswith('Loop'):
            # Update dictionary that counts number of loops on each thread
            currentThread = max(loopInThreadCounts.keys())
            loopInThreadCounts[currentThread] = loopInThreadCounts[currentThread] + 1

            # Test backwards to see if there are nodes between the loop start and the thread start
            inLoopWithNowtBefore = True
            for previousLine in reversed(lines[0:index]):
                if previousLine.startswith('Play') or previousLine.startswith('Pause') or previousLine.startswith('Loop') or previousLine.startswith('If'):
                    inLoopWithNowtBefore = False
                    break
                elif previousLine.startswith('Thread'):
                    break

            loopCount = loopCount + 1
            inLoop = inLoop + 1

            if inLoop > 1:
                code['nestedLoops'] = True

        elif line.startswith('End loop'):
            inLoop = inLoop - 1
            nodesAfterThisLoop = True

            # Test fowards to see if there are nodes between the loop end and the thread end
            for nextLine in lines[index:]:
                if nextLine.startswith('Play') or nextLine.startswith('Pause') or nextLine.startswith('Loop') or nextLine.startswith('If'):
                    break
                elif nextLine.startswith('End thread'):
                    nodesAfterThisLoop = False
                    break
            # Record if loop was on its own in the thread
            if inLoopWithNowtBefore and not nodesAfterThisLoop:
               code['loopNowtBeforeOrAfter'] = True
            elif nodesAfterThisLoop:
                code['followedLoops'] = True
            inLoopWithNowtBefore = False

        if 'constant' in line:
            code['constantsNoVariables'] = True

        if ('random' in line or 'infinity' in line) and 'x =' not in line:
            code['randomOrInfinityNoVariables'] = True

        if 'count up' in line or 'count down' in line:
            code['independentCounters'] = True

        if 'x = ' in line and 'x + 1' not in line and 'x - 1' not in line:
            code['variablesWithoutCounters'] = True

        if 'x = x + 1' in line or 'x = x - 1' in line:
            code['countersWithVariables'] = True

    # Set up the counts and the two sequence tests
    code['nodeCount'] = loopCount + playCount + pauseCount + selectionCount
    if (playCount > 0 or pauseCount > 0) and loopCount == 0 and selectionCount == 0:
        if code['threadCount'] > 1:
            code['multiThreadedSequences'] = True
        else:
            code['singleThreadedSequences'] = True

    # Count the threads with at least one loop
    loopInThreadCount = sum(value > 0 for value in loopInThreadCounts.values()) # int(True) == 1
    if loopInThreadCount > 1:
        code['loopsOnMultipleThreads'] = True

    return code


def ParseSessions(path):
    sessions = []

    # Read the sub directories
    subDirs = next(os.walk(path))[1]

    # Read and process the logs in each sub-directory
    for subDir in subDirs:

        # Read the log, code, and exception files so that we can ingest them
        loggedFileNames = [fileName for fileName in os.listdir(path + subDir + '\\Logs') if fileName.lower().endswith('txt')]

        # Run through the log files
        for logFileName in [fileName for fileName in loggedFileNames if fileName.lower().startswith('log')]:

            # Set up counts etc.
            currentSession = GetSession(subDir, logFileName)
            previousDuration = 0

            # Open the log file
            with io.open(path + subDir + '\\Logs\\' + logFileName, 'r', encoding='latin-1') as file:

                # Read the log file and split it into lines
                fileTextLines = file.read().split('\n')

                # Only bother with files that look like valid log files
                if len(fileTextLines) > 0 and fileTextLines[0].startswith('Log started: '):

                    # Process each line
                    for fileTextLine in fileTextLines:

                        # Parse out the duration
                        if 'StartPlaying' in fileTextLine or 'ReadCode' in fileTextLine:
                            match = re.search('\] \[([0-9]+)', fileTextLine)
                            if match != None:
                                candidateDuration = match.group(1)
                                if candidateDuration != '':
                                    durationInt = int(candidateDuration)

                                    if (durationInt - previousDuration) > maxSecondsGapInSession:
                                        # We need to start a new session
                                        AddSessionToCSV(currentSession, csvFileLines)
                                        newSession = GetSession(subDir, logFileName)
                                        newSession['start'] = currentSession['start']
                                        newSession['offset'] = durationInt
                                        currentSession = newSession
                                    else:
                                        # Set the offset to the first play or read in the log
                                        if currentSession['offset'] == 0:
                                            currentSession['offset'] = durationInt
                                        # Keep tally of the last play or read 
                                        currentSession['duration'] = durationInt

                                    # Record the duration for comparison with the next play or read
                                    previousDuration = durationInt

                        # Save the date and time
                        if fileTextLine.startswith('Log started: '):
                            currentSession['start'] = fileTextLine.replace('Log started: ', '')

                        # Increment the counts
                        if 'StartPlaying' in fileTextLine:
                            currentSession['numPlay'] = currentSession['numPlay'] + 1
                        if 'ReadCode' in fileTextLine:
                            currentSession['numRead'] = currentSession['numRead'] + 1

                        if 'StartPlaying' in fileTextLine or 'ReadCode' in fileTextLine:
                            # Find the code file name
                            match = re.search('(Code_[0-9]+-[0-9]+.txt)', fileTextLine)
                            if match != None:
                                candidateCodeFileName = match.group(1)
                                if candidateCodeFileName != '':
                                    # Load the code file
                                    with io.open(path + subDir + '\\Logs\\' + candidateCodeFileName, 'r', encoding='latin-1') as codeFile:
                                        codeFileLines = codeFile.read().split('\n')
                                        # Get the data from the code file
                                        code = ParseCodeFile(codeFileLines)
                                        # Combine the code file's data with the current session data
                                        currentSession['minNodeCount'] = min(currentSession['minNodeCount'], code['nodeCount'])
                                        currentSession['minThreadCount'] = min(currentSession['minThreadCount'], code['threadCount'])
                                        currentSession['maxNodeCount'] = max(currentSession['maxNodeCount'], code['nodeCount'])
                                        currentSession['maxThreadCount'] = max(currentSession['maxThreadCount'], code['threadCount'])
                                        currentSession['singleThreadedSequences'] = currentSession['singleThreadedSequences'] or code['singleThreadedSequences']
                                        currentSession['multiThreadedSequences'] = currentSession['multiThreadedSequences'] or code['multiThreadedSequences']
                                        currentSession['loopNowtBeforeOrAfter'] = currentSession['loopNowtBeforeOrAfter'] or code['loopNowtBeforeOrAfter']
                                        currentSession['followedLoops'] = currentSession['followedLoops'] or code['followedLoops']
                                        currentSession['loopsOnMultipleThreads'] = currentSession['loopsOnMultipleThreads'] or code['loopsOnMultipleThreads']
                                        currentSession['constantsNoVariables'] = currentSession['constantsNoVariables'] or code['constantsNoVariables']
                                        currentSession['randomOrInfinityNoVariables'] = currentSession['randomOrInfinityNoVariables'] or code['randomOrInfinityNoVariables']
                                        currentSession['manualSelection'] = currentSession['manualSelection'] or code['manualSelection']
                                        currentSession['selectionInLoop'] = currentSession['selectionInLoop'] or code['selectionInLoop']
                                        currentSession['independentCounters'] = currentSession['independentCounters'] or code['independentCounters']
                                        currentSession['variablesWithoutCounters'] = currentSession['variablesWithoutCounters'] or code['variablesWithoutCounters']
                                        currentSession['countersWithVariables'] = currentSession['countersWithVariables'] or code['countersWithVariables']
                                        currentSession['nestedLoops'] = currentSession['nestedLoops'] or code['nestedLoops']
            sessions.append(currentSession)
    return sessions


# Save the sessions to CSV
def SaveToCSV(sessions):
    csvFileLines = [ 'Name,LogFile,DateTime,Duration,PlayCount,ReadCount,MinNodeCount,MinThreadCount,MaxNodeCount,MaxThreadCount,SingleThreadedSequences,MultiThreadedSequences,LoopNowtBeforeOrAfter,FollowedLoops,LoopsOnMultipleThreads,ConstantsNoVariables,RandomOrInfinityNoVariables,ManualSelection,SelectionInLoop,IndependentCounters,VariablesWithoutCounters,CountersWithVariables,NestedLoops' ]
    AddSessionsToCSV(sessions, csvFileLines)
    with io.open(path + '\\Sessions.csv', 'w') as outputFile:
        mergedOutputLines = '\n'.join(csvFileLines)
        outputFile.writelines(mergedOutputLines)


def DeriveProgression(sessions):

