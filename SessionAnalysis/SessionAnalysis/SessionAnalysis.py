# Using Python 3.6

import os, io
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

        # Start the next line for the CSV file
        newLine = subDir + ","

        # Open the log file
        with io.open(path + subDir + "\\Logs\\" + logFileName, "r", encoding="latin-1") as file:

            # Read the log file and split it into lines
            fileTextLines = file.read().split('\n')

            if len(fileTextLines) > 0 and fileTextLines[0].startswith("Log started: "):

                # Save the date and time
                newLine = newLine + fileTextLines[0].replace("Log started: ", "") + ","

                # Count number of plays and reads
                numPlay = 0
                numRead = 0
                for fileTextLine in fileTextLines:
                    if "StartPlaying" in fileTextLine:
                        numPlay = numPlay + 1
                    if "ReadCode" in fileTextLine:
                        numRead = numRead + 1

                # Parse out the duration
                duration = ""
                for fileTextLine in reversed(fileTextLines):
                    if "] [" in fileTextLine:
                        secondsBit = fileTextLine.split("] [")[-1]
                        duration = secondsBit.split(".")[0]
                        break
                newLine = newLine + duration + "," + str(numPlay) + "," + str(numRead)

                # Add the new line to the CSV
                csvFileLines.append(newLine)

# Save the CSV to disk
with io.open(path + "\\Sessions.csv", "w") as outputFile:
    mergedOutputLines = "\n".join(csvFileLines)
    outputFile.writelines(mergedOutputLines)