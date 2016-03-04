import time
import Constraints
from Puzzle import SudokuPuzzle

class QueueItem:
    def __init__(self, row, column):
        if row < 1 or row > 9 or column < 1 or column > 9:
            raise ValueError('Sudoku only works 1-9');
        self.row = row
        self.column = column

MAX_SEARCH_DEPTH = 5

class Solver:
    def __init__(self, puzzle, depth=0):
        self.puzzle = puzzle
        if depth > MAX_SEARCH_DEPTH:
            raise Constraints.SudokuConstraintViolationError('max depth reached')
        self.depth = depth
        self.queue = []
        self.constraintQueue = []
        self.constraintQueue.append(Constraints.NoRowDuplicates(self.puzzle))
        self.constraintQueue.append(Constraints.NoColumnDuplicates(self.puzzle))
        self.constraintQueue.append(Constraints.NoBoxDuplicates(self.puzzle))
        self.constraintQueue.append(Constraints.ProcessOfElimination(self.puzzle))
        
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
        print 'solving...'
        time_start = time.time()
        # enqueue all InitialSquare objects
        for i in range(1,10):
            for j in range(1,10):
                if self.puzzle.getSquare(i,j).hasSingleValue():
                    queueItem = QueueItem(i,j)
                    self.enqueue(queueItem)
        # clean all squares
        self.cleanAll()
        print 'queue length:' + str(len(self.queue))
        MAX_RUNS = 30
        for run in range(0, MAX_RUNS):
            print 'run ' + str(run) + ': queue length = ' + str(len(self.queue))
            if len(self.queue) == 0:
                #
                # Search/look-ahead goes here
                #
                print 'empty queue, depth: ' + str(self.depth) + ', run: ' + str(run)
                self.puzzle.printPuzzle()
                # a complete guess list, ordered by degree ascending
                # one guess is (i, j, value)
                guessList = self.guessList()
                # note there should be many correct guesses - one per node!
                correctGuess = None
                for guess in guessList:
                    i = guess[0]
                    j = guess[1]
                    value = guess[2]
                    print 'guess: (i,j,value)=(%d,%d,%d)' % (i,j,value)
                    # clone the puzzle
                    puzzleClone = SudokuPuzzle(self.puzzle.initialStrings)
                    # apply the guess
                    puzzleClone.getSquare(i,j).select(value)
                    # update the initial strings
                    c = puzzleClone.initialStrings[i-1][j-1]
                    if not c == ' ':
                        raise Constraints.SudokuConstraintViolationError('should be empty')
                    # strings and tuples are immutable
                    rowstring = puzzleClone.initialStrings[i-1]
                    rowlist = list(rowstring)
                    rowlist[j-1] = str(value)
                    newrowstring = "".join(rowlist)
                    tupleaslist = list(puzzleClone.initialStrings)
                    tupleaslist[i-1]=newrowstring
                    puzzleClone.initialStrings = tuple(tupleaslist)
                    # strings and tuples are immutable
                    # and solve
                    puzzleClone.printPuzzle()
                    newSolver = Solver(puzzleClone, self.depth+1)
                    try:
                        possibleSolution = newSolver.solve()
                    except Constraints.SudokuConstraintViolationError:
                        print 'not right'
                        continue
                    print 'right'
                    correctGuess = guess
                    break
                if correctGuess is None:
                    raise Constraints.SudokuConstraintViolationError('no guesses??')
                # apply the guess and continue
                i = correctGuess[0]
                j = correctGuess[1]
                value = correctGuess[2]
                print 'applying (i,j,value) = (%d,%d,%d)' % (i,j,value)
                self.puzzle.getSquare(i,j).select(value)
                print 'enqueue all dirty, mark clean, continuing'
                self.enqueueAllDirtyAndMarkClean()
                continue
            # run through queue completely
            while len(self.queue) > 0:
                queueItem = self.queue.pop()
                self.process(queueItem)
            if self.doneYet():
                print 'done!'
                self.puzzle.printPuzzle()
                break
            self.enqueueAllDirtyAndMarkClean()
        time_end = time.time()
        print 'solving finished, elapsed time = ' + str(time_end-time_start)
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
    def doneYet(self):
        for i in range(1,10):
            for j in range(1,10):
                if not self.puzzle.getSquare(i,j).hasSingleValue():
                    return False
        self.validateSolution()
        return True
    pass
