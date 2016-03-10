import Constraints
import copy

class Square:
    "Superclass for initial and derived squares"
    def __init__(self):
        raise TypeError('abstract class, do not instantiate')
    pass

class InitialSquare(Square):
    "Initial square, given by the problem"
    def __init__(self, value):
        if value < 1 or value > 9:
            raise ValueError('Sudoku only works 1-9');
        self.value = value
        #self.__possibleValues = [0] * 9
        #self.__possibleValues[value-1] = 1
    def countRemaining(self):
        return 1
    def hasSingleValue(self):
        return True
    def getSingleValue(self):
        return self.value
    def eliminate(self, arg):
        pass
    def bitmapElimination(self, bitmap):
        pass
    def select(self, arg):
        pass
    def isDirty(self):
        return False
    def clean(self):
        pass
    def isPossible(self, value):
        return self.value == value
    def valuesRemaining(self):
        return (self.value,)
    def getBitmap(self):
        return BITMAP_VALUES[self.value]
    pass

# 111111111 == 511
# first value is the ALL value to enable indexing by Sudoku value
# (avoiding 0-index vs 1-index)
BITMAP_VALUES = (511, 1, 2, 4, 8, 16, 32, 64, 128, 256)

class DerivedSquare(Square):
    "Derived square, initially empty"
    def __init__(self, initialState = None):
        if initialState is None:
            self.__bitmap = BITMAP_VALUES[0]
        else:
            self.__bitmap = initialState
        self.__singleValue = None
        self.dirty = False
    def countRemaining(self):
        return self.__numberOfBits(self.__bitmap)
    def __numberOfBits(self, bitmap):
        if bitmap == 0:
            return 0
        # 1000 x
        # 0111 x-1
        # x & x-1 = 0
        # is x & x-1 always smaller?
        # is the number of bit of (x & x-1) always 1 less?
        # seems to be yes and yes
        return 1 + self.__numberOfBits(bitmap & bitmap-1)
    def hasSingleValue(self):
        return self.countRemaining() is 1
    def getSingleValue(self):
        if not self.hasSingleValue():
            raise ValueError('do not call getSingleValue if no single value!')
        if self.__singleValue is None:
            self.__singleValue = self.__calculateSingleValue()
        return self.__singleValue
    def __calculateSingleValue(self):
        for possibleValue in range(1,10):
            if self.isPossible(possibleValue):
                return possibleValue
        raise ValueError('should not get here')
    def isPossible(self, value):
        return (self.__bitmap & BITMAP_VALUES[value]) != 0
    def __copyStateFrom_deprecate(self, otherSquare):
        keep = otherSquare.valuesRemainingUnsorted()
        self.__possibleValues = set(keep)
    def __valuesRemainingUnsorted_deprecate(self):
        return tuple(self.__possibleValues)
    def getBitmap(self):
        return self.__bitmap
    def valuesRemaining(self):
        'returns a sorted tuple of possible values'
        valueList = []
        for possibleValue in range(1, 10):
            if self.isPossible(possibleValue):
                valueList.append(possibleValue)
        return tuple(valueList)
    def select(self, arg):
        previous_bitmap = self.__bitmap
        self.__bitmap = self.__bitmap & BITMAP_VALUES[arg]
        if self.__bitmap == 0:
            raise Constraints.SudokuConstraintViolationError('cannot select')
        if previous_bitmap != self.__bitmap:
            self.dirty = True
    def bitmapElimination(self, bitmap):
        previous_bitmap = self.__bitmap
        self.__bitmap = self.__bitmap & (BITMAP_VALUES[0] ^ bitmap)
        if previous_bitmap != self.__bitmap:
            self.dirty = True
    def eliminate(self, arg):
        "eliminate singly or in bulk"
        if isinstance(arg, list):
            for item in arg:
                self.eliminate(item)
        else:
            if arg < 1 or arg > 9:
                raise ValueError('Sudoku only works 1-9: ' + str(arg));
            self.bitmapElimination(BITMAP_VALUES[arg])
    def isDirty(self):
        return self.dirty
    
    def clean(self):
        self.dirty = False
        return
