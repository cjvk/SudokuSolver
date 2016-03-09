import Profiler

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
            twoValuesRemaining = constraintSquare.valuesRemaining()
            othersquares = f(self.puzzle, queueItem)
            for i in range(0, len(othersquares)):
                if othersquares[i].valuesRemaining() == twoValuesRemaining:
                    # bingo!
                    for j in range(0, len(othersquares)):
                        if i != j:
                            othersquares[j].eliminate(list(twoValuesRemaining))

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

class NoRowDuplicates(Constraint):
    def process(self, queueItem):
        row = queueItem.row
        col = queueItem.column
        if self.puzzle.getSquare(row,col).hasSingleValue():
            val = self.puzzle.getSquare(row,col).getSingleValue()
            for square in rowSquares8(self.puzzle, queueItem):
                square.eliminate(val)
class NoColumnDuplicates(Constraint):
    def process(self, queueItem):
        row = queueItem.row
        col = queueItem.column
        if self.puzzle.getSquare(row,col).hasSingleValue():
            val = self.puzzle.getSquare(row,col).getSingleValue()
            for square in columnSquares8(self.puzzle, queueItem):
                square.eliminate(val)
class NoBoxDuplicates(Constraint):
    def process(self, queueItem):
        row = queueItem.row
        col = queueItem.column
        if self.puzzle.getSquare(row,col).hasSingleValue():
            val = self.puzzle.getSquare(row,col).getSingleValue()
            for square in boxSquares8(self.puzzle, queueItem):
                square.eliminate(val)

class ProcessOfElimination(Constraint):
    def process(self, queueItem):
        Profiler.startStopWatch('constraints > ProcessOfElimination')
        # deduction within my row, column, box
        for value in range(1,10):
            for f in (rowSquares9, columnSquares9, boxSquares9):
                squaresWithValuePossible = []
                for square in f(self.puzzle, queueItem):
                    if square.isPossible(value):
                        squaresWithValuePossible.append(square)
                if len(squaresWithValuePossible) == 0:
                    Profiler.stopStopWatch('constraints > ProcessOfElimination')
                    raise SudokuConstraintViolationError('contradiction')
                elif len(squaresWithValuePossible) == 1:
                    squaresWithValuePossible[0].select(value)
                else:
                    pass
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


