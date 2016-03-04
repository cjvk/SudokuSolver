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
    def reset(self):
        pass
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
        print 'this should not be called, but return a value anyway'
        return (self.value,)
    pass

class DerivedSquare(Square):
    "Derived square, initially empty"
    def __init__(self):
        self.__possibleValues = [1] * 9
        self.dirty = False
    def reset(self):
        self.__init__()
    def countRemaining(self):
        return self.__possibleValues.count(1)
    def hasSingleValue(self):
        return self.countRemaining() is 1
    def getSingleValue(self):
        if not self.hasSingleValue():
            raise ValueError('do not call getSingleValue if no single value!')
        index = self.__possibleValues.index(1)
        return index + 1
    def isPossible(self, value):
        index = value - 1
        return self.__possibleValues[index] == 1
    def valuesRemaining(self):
        valueList = []
        for value in range(1,10):
            if self.isPossible(value):
                valueList.append(value)
        return tuple(valueList)
    def select(self, arg):
        eliminationList = list(range(1,10))
        eliminationList.remove(arg)
        self.eliminate(eliminationList)
    def eliminate(self, arg):
        "eliminate singly or in bulk; return true if values changed"
        if isinstance(arg, list):
            for item in arg:
                self.eliminate(item)
            return self.dirty
        else:
            if arg < 1 or arg > 9:
                raise ValueError('Sudoku only works 1-9');
            index = arg - 1
            if self.__possibleValues[index] == 1:
                self.__possibleValues[index] = 0
                self.dirty = True
    def isDirty(self):
        return self.dirty
    
    def clean(self):
        self.dirty = False
        return
