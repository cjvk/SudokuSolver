import Profiler
import Squares

class SudokuConstraintViolationError(RuntimeError):
    pass

class Constraint:
    def __init__(self, puzzle):
        self.puzzle = puzzle

class DoubleDouble(Constraint):
    def processInternal(self, queueItem, f):
        row = queueItem.row
        col = queueItem.column
        constraintSquare = self.puzzle.getSquare(row,col)
        if constraintSquare.countRemaining() is 2:
            constraintSquareState = constraintSquare.getBitmap()
            othersquares = f(self.puzzle, queueItem)
            for i in range(0, len(othersquares)):
                if othersquares[i].getBitmap() == constraintSquareState:
                    # bingo!
                    for j in range(0, len(othersquares)):
                        if i != j:
                            othersquares[j].bitmapElimination(constraintSquareState)
class DoubleDoubleBox(DoubleDouble):
    def process(self, queueItem):
        self.processInternal(queueItem, boxSquares8)

class DoubleDoubleColumn(DoubleDouble):
    def process(self, queueItem):
        self.processInternal(queueItem, columnSquares8)

class DoubleDoubleRow(DoubleDouble):
    def process(self, queueItem):
        self.processInternal(queueItem, rowSquares8)

class AllCannotBeEliminated(Constraint):
    def process(self, queueItem):
        row = queueItem.row
        col = queueItem.column
        if self.puzzle.getSquare(row,col).countRemaining() is 0:
            raise SudokuConstraintViolationError('contradiction')
class NoDuplicates(Constraint):
    def processInternal(self, queueItem, f):
        row = queueItem.row
        col = queueItem.column
        if self.puzzle.getSquare(row,col).hasSingleValue():
            for square in f(self.puzzle, queueItem):
                square.bitmapElimination(self.puzzle.getSquare(row,col).getBitmap())
class NoRowDuplicates(NoDuplicates):
    def process(self, queueItem):
        self.processInternal(queueItem, rowSquares8)
class NoColumnDuplicates(NoDuplicates):
    def process(self, queueItem):
        self.processInternal(queueItem, columnSquares8)
class NoBoxDuplicates(NoDuplicates):
    def process(self, queueItem):
        self.processInternal(queueItem, boxSquares8)

class ProcessOfElimination(Constraint):
    def process(self, queueItem):
        Profiler.startStopWatch('constraints > ProcessOfElimination')
        # deduction within my row, column, box
        for f in (rowSquares9, columnSquares9, boxSquares9):
            bitmaps = []
            squares = f(self.puzzle, queueItem)
            for square in squares:
                bitmaps.append(square.getBitmap())
            # e.g. in 4-sudoku, you have (23) (24) (1234) (34), you would select 1
            # given a number of bitmaps, how to count if certain position has
            # exactly 1 member set? Using bit operations
            # translate above to (0110) (0101) (1111) (0011)
            setEver = 0
            setOdd = 0
            setTwoPlusTimes = 0
            for bitmap in bitmaps:
                setEver = setEver | bitmap
                setOdd = setOdd ^ bitmap
                # first occurrence of 2 is setEver = 1, setOdd = 0
                setTwoPlusTimes = setTwoPlusTimes | (setEver & (~setOdd & 511))
            if setEver != 511:
                Profiler.stopStopWatch('constraints > ProcessOfElimination')
                raise SudokuConstraintViolationError('contradiction')
            # to get "Sudoku not", do bitwise not, then and with 511
            setExactlyOnce = setOdd & (511 & ~setTwoPlusTimes)
            # setExactlyOnce is values with exactly one square of legality
            for possibleValue in range(1,10):
                if Squares.BITMAP_VALUES[possibleValue] & setExactlyOnce != 0:
                    # find the square with possibleValue legal
                    found = False
                    for square in squares:
                        if square.isPossible(possibleValue):
                            found = True
                            square.select(possibleValue)
                            break
                    if not found:
                        Profiler.stopStopWatch('constraints > ProcessOfElimination')
                        # may not be found in case where a square was
                        # selected in above for loop, thereby eliminating
                        # some other potential value
                        # (resulting in a contradiction)
                        raise SudokuConstraintViolationError('should be found')
        Profiler.stopStopWatch('constraints > ProcessOfElimination')
class PairProcessOfElimination(Constraint):
    """
    (The pair version)
    For example, in a box suppose squares i and j are the only
    two squares which can have values v1 and v2. In other words,
    v1 and v2 have been eliminated as possibilities for all
    other squares.
    Then, you can eliminate all other values for those squares
    besides v1 and v2.

    This differs from DoubleDoubleBox et al because those
    examine for equality two squares and do not look at other
    squares, whereas this one does not look at the entirety
    of any square's allowed values and does look at other
    squares allowed values, within the box.

    This constraint would work in tandem with the DoubleDouble
    family of constraints, because the elimination marks as
    dirty, and the DoubleDouble family would reduce further.

    3/15/2016: Given the strategy of guessing first in these
               "pair nodes" is worse than simply guessing in
               the 2-9 range, and given that this constraint
               is MUCH more computationally intensive than
               doing the guess and propagating, I have chosen
               to not include this constraint in the simulation.
    """
    def process(self, queueItem):
        for value1 in range(1,10):
            for value2 in range(1,10):
                if value1 == value2:
                    continue
                for f in (rowSquares9, columnSquares9, boxSquares9):
                    squaresWithValue1Possible = []
                    squaresWithValue2Possible = []
                    for square in f(self.puzzle, queueItem):
                        if square.isPossible(value1):
                            squaresWithValue1Possible.append(square)
                        if square.isPossible(value2):
                            squaresWithValue2Possible.append(square)
                    len1 = len(squaresWithValue1Possible)
                    len2 = len(squaresWithValue2Possible)
                    if len1 == 2 and len2 == 2:
                        s1 = squaresWithValue1Possible
                        s2 = squaresWithValue2Possible
                        if s1[0] == s2[0] and s1[1] == s2[1]:
                            eliminateThese = list(range(1,10))
                            eliminateThese.remove(value1)
                            eliminateThese.remove(value2)
                            for porfin in s1:
                                porfin.eliminate(eliminateThese)
    pass

def rowSquares8(puzzle, queueItem):
    squareList = []
    for j in range(1,10):
        if j != queueItem.column:
            squareList.append(puzzle.getSquare(queueItem.row,j))
    return squareList
def rowSquares9(puzzle, queueItem):
    squareList = []
    for j in range(1,10):
        squareList.append(puzzle.getSquare(queueItem.row,j))
    return squareList
def columnSquares8(puzzle, queueItem):
    squareList = []
    for i in range(1, 10):
        if i != queueItem.row:
            squareList.append(puzzle.getSquare(i,queueItem.column))
    return squareList
def columnSquares9(puzzle, queueItem):
    squareList = []
    for i in range(1, 10):
        squareList.append(puzzle.getSquare(i,queueItem.column))
    return squareList
def boxSquares8(puzzle, queueItem):
    squareList = []
    boxi = ((queueItem.row-1)/3)+1
    boxj = ((queueItem.column-1)/3)+1
    triples = {
        1 : (1,2,3),
        2 : (4,5,6),
        3 : (7,8,9)
    }
    rows = list(triples[boxi])
    cols = list(triples[boxj])
    for i in rows:
        for j in cols:
            if i != queueItem.row or j != queueItem.column:
                squareList.append(puzzle.getSquare(i,j))
    return squareList
def boxSquares9(puzzle, queueItem):
    squareList = []
    boxi = ((queueItem.row-1)/3)+1
    boxj = ((queueItem.column-1)/3)+1
    triples = {
        1 : (1,2,3),
        2 : (4,5,6),
        3 : (7,8,9)
    }
    rows = list(triples[boxi])
    cols = list(triples[boxj])
    for i in rows:
        for j in cols:
            squareList.append(puzzle.getSquare(i,j))
    return squareList


