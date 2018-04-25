# Using Python 3.6

import os, io, re
from functools import reduce

path = "F:\\Users\\timregan\\Microsoft\\ProjectTorino - Logs from Trialists\\"
csvFileLines = [ "Name,DateTime,Duration,PlayCount,ReadCount" ]

# Read the sub directories
subDirs = next(os.walk(path))[1]

# Read and process the logs in each sub-directory
for subDir in subDirs:

    # Read the log, code, and exception files so that we can ingest them
    loggedFileNames = [fileName for fileName in os.listdir(path + subDir + "\\Logs") if fileName.lower().endswith("txt")]

    # Run through the log files
    for logFileName in [fileName for fileName in loggedFileNames if fileName.lower().startswith("log")]:

        # Set up counts etc.
        numPlay = 0
        numRead = 0
        dateTime = ""
        duration = ""

        # Open the log file
        with io.open(path + subDir + "\\Logs\\" + logFileName, "r", encoding="latin-1") as file:

            # Read the log file and split it into lines
            fileTextLines = file.read().split('\n')

            if len(fileTextLines) > 0 and fileTextLines[0].startswith("Log started: "):

                # Process each line
                for fileTextLine in fileTextLines:

                    # Save the date and time
                    if fileTextLine.startswith("Log started: "):
                        dateTime = fileTextLine.replace("Log started: ", "")

                    # Increment the counts
                    if "StartPlaying" in fileTextLine:
                        numPlay = numPlay + 1
                    if "ReadCode" in fileTextLine:
                        numRead = numRead + 1

                    # Parse out the duration
                    match = re.search("\] \[([0-9]+)", fileTextLine)
                    if match != None:
                        candidateDuration = match.group(1)
                        if candidateDuration != "":
                            duration = candidateDuration

                    # TODO: If too much time has passed start a new session
                    # TODO: Load the coad file and keep maxumum number of nodes and list of node types

        # Add the new line to the CSV
        if dateTime != "" and duration != "":
            csvFileLines.append(subDir + "," + dateTime + "," + duration + "," + str(numPlay) + "," + str(numRead))

# Save the CSV to disk
with io.open(path + "\\Sessions.csv", "w") as outputFile:
    mergedOutputLines = "\n".join(csvFileLines)
    outputFile.writelines(mergedOutputLines)