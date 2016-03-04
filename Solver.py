import time
import Constraints
from Puzzle import SudokuPuzzle

class QueueItem:
    def __init__(self, row, column):
        if row < 1 or row > 9 or column < 1 or column > 9:
            raise ValueError('Sudoku only works 1-9');
        self.row = row
        self.column = column

MAX_SEARCH_DEPTH = 20
TOTAL_GUESSES_MADE = 0

class Progress:
    def __init__(self, depth=0):
        # depth is 0-indexed
        self.depth = depth
        self.guesses = None
        # currentGuessIndex is 0-indexed
        self.currentGuessIndex = None

class Solver:
    def __init__(self, puzzle, progressTuple=None):
        self.puzzle = puzzle
        if progressTuple is None:
            self.progressTuple = (Progress(),)
        else:
            tempProgressList = []
            for pt in progressTuple:
                ptcopy = Progress(pt.depth)
                ptcopy.currentGuessIndex = pt.currentGuessIndex
                tempGuessList = []
                for ptguess in pt.guesses:
                    ptguesscopy = (ptguess[0], ptguess[1], ptguess[2])
                    tempGuessList.append(ptguesscopy)
                ptcopy.guesses = tuple(tempGuessList)
                tempProgressList.append(ptcopy)
            tempProgressList.append(Progress(len(progressTuple)))
            self.progressTuple = tuple(tempProgressList)
        if self.progressTuple[len(self.progressTuple)-1].depth > MAX_SEARCH_DEPTH:
            raise Constraints.SudokuConstraintViolationError('max depth reached')
        self.queue = []
        self.constraintQueue = []
        self.constraintQueue.append(Constraints.NoRowDuplicates(self.puzzle))
        self.constraintQueue.append(Constraints.NoColumnDuplicates(self.puzzle))
        self.constraintQueue.append(Constraints.NoBoxDuplicates(self.puzzle))
        self.constraintQueue.append(Constraints.ProcessOfElimination(self.puzzle))
        self.constraintQueue.append(Constraints.AllCannotBeEliminated(self.puzzle))
        self.constraintQueue.append(Constraints.DoubleDoubleRow(self.puzzle))
        self.constraintQueue.append(Constraints.DoubleDoubleColumn(self.puzzle))
        self.constraintQueue.append(Constraints.DoubleDoubleBox(self.puzzle))
    def getDepth(self):
        return self.progressTuple[len(self.progressTuple)-1].depth
    def getProgress(self):
        return self.progressTuple[len(self.progressTuple)-1]
    def process(self, queueItem):
        for constraint in self.constraintQueue:
            constraint.process(queueItem)
        pass

    def solve(self):
        """
        1) enqueue all InitialSquare objects
        2) clean all squares
        3) if queue empty, exit; otherwise
           a. run through queue completely
           b. check if done
           c. enqueue any square which is dirty (and clean square)
           d. go to 3)
        """
        global TOTAL_GUESSES_MADE
        debug('solving... %s' % str(self.searchStatusString()))
        time_start = time.time()
        # enqueue all InitialSquare objects
        for i in range(1,10):
            for j in range(1,10):
                if self.puzzle.getSquare(i,j).hasSingleValue():
                    queueItem = QueueItem(i,j)
                    self.enqueue(queueItem)
        # clean all squares
        self.cleanAll()
        debug('queue length:' + str(len(self.queue)))
        MAX_RUNS = 30
        for run in range(0, MAX_RUNS):
            debug('depth: %d, run: %d, queue length: %d' % (
                self.getDepth(), run, len(self.queue)))
            if len(self.queue) == 0:
                #
                # Search/look-ahead goes here
                #
                debug('empty queue, depth: ' + str(self.getDepth()) + ', run: ' + str(run))
                debugPrintPuzzle(self.puzzle)
                # a complete guess list, ordered by degree ascending
                # one guess is (i, j, value)
                guessList = self.guessList()
                self.getProgress().guesses = guessList
                # note there should be many correct guesses - one per node!
                correctGuess = None
                for index in range(0, len(guessList)):
                    guess = guessList[index]
                    self.getProgress().currentGuessIndex = index
                    i = guess[0]
                    j = guess[1]
                    value = guess[2]
                    debug('guess: (i,j,value)=(%d,%d,%d)' % (i,j,value))
                    # clone the puzzle
                    puzzleClone = SudokuPuzzle(self.puzzle.initialStrings)
                    # copy the state of all the squares
                    for ii in range(1,10):
                        for jj in range(1,10):
                            mysquare = self.puzzle.getSquare(ii,jj)
                            clonesquare = puzzleClone.getSquare(ii,jj)
                            clonesquare.copyStateFrom(mysquare)
                    # apply the guess
                    puzzleClone.getSquare(i,j).select(value)
                    TOTAL_GUESSES_MADE = TOTAL_GUESSES_MADE + 1
                    # and solve
                    debugPrintPuzzle(puzzleClone)
                    newSolver = Solver(puzzleClone, self.progressTuple)
                    try:
                        possibleSolution = newSolver.solve()
                    except Constraints.SudokuConstraintViolationError:
                        #debug('not right')
                        self.puzzle.getSquare(i,j).eliminate(value)
                        continue
                    print 'right'
                    # possibleSolution seems to have the correct solution
                    # just returning it isn't enough maybe
                    # I need to copy the solution!
                    self.copyFromSolution(possibleSolution)
                    correctGuess = guess
                    break
                if correctGuess is None:
                    raise Constraints.SudokuConstraintViolationError('guesses all wrong')
                # apply the guess and continue
                # this logic is kind of wrong - it seriously
                # re-does a ton of work
                i = correctGuess[0]
                j = correctGuess[1]
                value = correctGuess[2]
                debug('applying (i,j,value) = (%d,%d,%d)' % (i,j,value))
                self.puzzle.getSquare(i,j).select(value)
                debug('enqueue all dirty, mark clean, continuing')
                self.enqueueAllDirtyAndMarkClean()
                continue
            # run through queue completely
            while len(self.queue) > 0:
                queueItem = self.queue.pop()
                self.process(queueItem)
            if self.doneYet():
                print 'done!'
                # arguably this should short circuit to the original caller
                break
            self.enqueueAllDirtyAndMarkClean()
        time_end = time.time()
        args = (time_end-time_start, TOTAL_GUESSES_MADE)
        print 'solving finished, elapsed time = %f, %d total guesses' % args
        return self.puzzle
    def enqueueAllDirtyAndMarkClean(self):
        for i in range(1,10):
            for j in range(1,10):
                if self.puzzle.getSquare(i,j).isDirty():
                    queueItem = QueueItem(i,j)
                    self.enqueue(queueItem)
                    self.puzzle.getSquare(i,j).clean()
    def guessList(self):
        "return a complete guess list, ordered by degree ascending"
        # a single guess is a tuple (i, j, value)
        guessList = []
        for degree in range(2,10): # 2-9
            for i in range(1,10):
                for j in range(1,10):
                    square = self.puzzle.getSquare(i,j)
                    if square.countRemaining() == degree:
                        for value in square.valuesRemaining():
                            guessList.append((i,j,value))
        return guessList
    def cleanAll(self):
        for i in range(1,10):
            for j in range(1,10):
                self.puzzle.getSquare(i,j).clean()
    def enqueue(self, queueItem):
        self.queue.append(queueItem)
    def copyFromSolution(self, possibleSolution):
        for i in range(1,10):
            for j in range(1,10):
                correctValue = possibleSolution.getSquare(i,j).getSingleValue()
                self.puzzle.getSquare(i,j).select(correctValue)
        self.validateSolution()
    def validateSolution(self):
        validationError = Constraints.SudokuConstraintViolationError('validation failure')
        # validate rows
        for row in range(1,10):
            rowList = Constraints.rowSquares9(self.puzzle, QueueItem(row,1))
            valuesDict = {}
            for square in rowList:
                value = square.getSingleValue()
                if value in valuesDict:
                    raise validationError
                valuesDict[value] = True
            for value in range(1,10):
                if not value in valuesDict:
                    raise validationError
        # validate columns
        for col in range(1,10):
            colList = Constraints.columnSquares9(self.puzzle, QueueItem(1,col))
            valuesDict = {}
            for square in colList:
                value = square.getSingleValue()
                if value in valuesDict:
                    raise validationError
                valuesDict[value] = True
            for value in range(1,10):
                if not value in valuesDict:
                    raise validationError
        # validate boxes
        allBoxes = (
            QueueItem(1,1),QueueItem(1,4),QueueItem(1,7),
            QueueItem(4,1),QueueItem(4,4),QueueItem(4,7),
            QueueItem(7,1),QueueItem(7,4),QueueItem(7,7),
        )
        for queueItemBox in allBoxes:
            boxList = Constraints.boxSquares9(self.puzzle, queueItemBox)
            valuesDict = {}
            for square in boxList:
                value = square.getSingleValue()
                if value in valuesDict:
                    raise validationError
                valuesDict[value] = True
            for value in range(1,10):
                if not value in valuesDict:
                    raise validationError
    def searchStatusString(self):
        '10.62% completed, 103330 guesses made'
        # depth 0, 2 guesses, on guess 1 (last one!)
        # 50% done
        # depth 1, 3 guesses, on guess 1 (0-1-2) (second one)
        # 1/2 * 1/3 = 16% additional
        # depth 2, 10 guesses, on guess 6
        # 1/2 * 1/3 * 6/10 = 10% additional
        percentageDone = 0.0
        factor = 1.0
        for progress in self.progressTuple:
            depth = progress.depth
            if progress.guesses is None or progress.currentGuessIndex is None:
                continue
            numerator = progress.currentGuessIndex
            denominator = len(progress.guesses)
            additionalPercentage = (float(numerator) / denominator) * factor
            percentageDone += additionalPercentage
            factor = factor / denominator
        # multiply by 100
        percentageDone *= 100
        s = "%6.20f completed, %d guesses made" % (percentageDone, TOTAL_GUESSES_MADE)
        if (TOTAL_GUESSES_MADE % 10000) == 0:
            #self.breakpoint()
            pass
        return s
    def breakpoint(self):
        keypress = raw_input("Press Enter to continue, q to quit: ")
        if keypress == 'q' or keypress == 'Q':
            exit()
    def doneYet(self):
        for i in range(1,10):
            for j in range(1,10):
                if not self.puzzle.getSquare(i,j).hasSingleValue():
                    return False
        self.validateSolution()
        return True
    pass

PRINT_EVERY_N_GUESSES = 1000
def debug(str):
    if (TOTAL_GUESSES_MADE % PRINT_EVERY_N_GUESSES) == 0:
        print str
PRINT_PUZZLE_EVERY_N_GUESSES = 10000
def debugPrintPuzzle(puzzle):
    if (TOTAL_GUESSES_MADE % PRINT_PUZZLE_EVERY_N_GUESSES) == 0:
        puzzle.printPuzzle()
