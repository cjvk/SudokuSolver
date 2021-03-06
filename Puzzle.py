from Squares import Square
from Squares import InitialSquare
from Squares import DerivedSquare
import Profiler

class SudokuPuzzle:
    def __validateInitialStrings(self, initialStrings):
        if not isinstance(initialStrings, (list, tuple)):
            raise ValueError('Puzzle description must be list or tuple')
        if len(initialStrings) != 9:
            raise ValueError('Sudoku has 9 rows')
        for initialString in initialStrings:
            if len(initialString) != 9:
                raise ValueError('Sudoku has 9 columns')
        return
    def __calculateRowsFromInitialStrings(self, initialStrings):
        rows = []
        for initialString in initialStrings:
            row = []
            for c in initialString:
                if c == " ":
                    row.append(DerivedSquare())
                else:
                    row.append(InitialSquare(int(c)))
            rows.append(row)
        return rows
    def __init__(self, initialStrings, byHand = False):
        self.initialStrings = initialStrings
        if not byHand:
            self.__validateInitialStrings(initialStrings)
            self.rows = self.__calculateRowsFromInitialStrings(initialStrings)
    def cloneFrom(self, fromPuzzle):
        self.rows = []
        for i in range(1,10):
            row = []
            for j in range(1,10):
                fromSquare = fromPuzzle.getSquare(i,j)
                if isinstance(fromSquare,DerivedSquare):
                    newSquare = DerivedSquare(fromSquare.getBitmap())
                    row.append(newSquare)
                else:
                    # InitialSquare
                    row.append(InitialSquare(fromSquare.getSingleValue()))
            self.rows.append(row)
    def getSquare(self, row, column):
        rowIndex = row - 1
        columnIndex = column - 1
        square = self.rows[rowIndex][columnIndex]
        return square
    def printPuzzle(self):
        print '-----------'
        for row in self.rows:
            rowString = '|'
            for square in row:
                if square.hasSingleValue():
                    rowString += str(square.getSingleValue())
                else:
                    rowString += ' '
            rowString += '|'
            print rowString
        print '-----------'
