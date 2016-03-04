class SudokuConstraintViolationError(RuntimeError):
    pass

class Constraint:
    def __init__(self, puzzle):
        self.puzzle = puzzle
    
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
        # deduction within my row, column, box
        for value in range(1,10):
            for f in (rowSquares9, columnSquares9, boxSquares9):
                squaresWithValuePossible = []
                for square in f(self.puzzle, queueItem):
                    if square.isPossible(value):
                        squaresWithValuePossible.append(square)
                if len(squaresWithValuePossible) == 0:
                    raise SudokuConstraintViolationError('contradiction')
                elif len(squaresWithValuePossible) == 1:
                    squaresWithValuePossible[0].select(value)
                else:
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

