import Constraints

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
        self.__possibleValues = [0] * 9
        self.__possibleValues[value-1] = 1
    def countRemaining(self):
        return 1
    def hasSingleValue(self):
        return True
    def getSingleValue(self):
        return self.value
    def eliminate(self, arg):
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
    def copyStateFrom(self, otherSquare):
        pass
    pass

class DerivedSquare(Square):
    "Derived square, initially empty"
    def __init__(self):
        self.__possibleValues = set(range(1,10))
        self.__singleValue = None
        self.dirty = False
    def countRemaining(self):
        return len(self.__possibleValues)
    def hasSingleValue(self):
        return self.countRemaining() is 1
    def getSingleValue(self):
        if not self.hasSingleValue():
            raise ValueError('do not call getSingleValue if no single value!')
        if self.__singleValue is None:
            self.__singleValue = self.__calculateSingleValue()
        return self.__singleValue
    def __calculateSingleValue(self):
        return next(iter(self.__possibleValues))
    def isPossible(self, value):
        return value in self.__possibleValues
    def copyStateFrom(self, otherSquare):
        keep = otherSquare.valuesRemaining()
        self.__possibleValues = set(keep)
    def valuesRemaining(self):
        'returns a sorted tuple of possible values'
        # return tuple(self.__possibleValues)
        valueList = list(self.__possibleValues)
        valueList.sort()
        return tuple(valueList)
    def select(self, arg):
        if not self.isPossible(arg):
            raise Constraints.SudokuConstraintViolationError('cannot select')
        markAsDirty = not self.hasSingleValue()
        self.__possibleValues = set((arg,))
        if markAsDirty:
            self.dirty = True
    def eliminate(self, arg):
        "eliminate singly or in bulk"
        if isinstance(arg, list):
            for item in arg:
                self.eliminate(item)
        else:
            if arg < 1 or arg > 9:
                raise ValueError('Sudoku only works 1-9: ' + str(arg));
            if arg in self.__possibleValues:
                self.__possibleValues.remove(arg)
                self.dirty = True
    def isDirty(self):
        return self.dirty
    
    def clean(self):
        self.dirty = False
        return
