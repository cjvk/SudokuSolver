# let's figure levels of 1-5, with 0 representing "always print"
DEBUG = 1

def debug(str, loglevel=3):
    if loglevel <= DEBUG:
        print str

def debugPrintPuzzle(puzzle, loglevel=3):
    if loglevel <= DEBUG:
        puzzle.printPuzzle()
