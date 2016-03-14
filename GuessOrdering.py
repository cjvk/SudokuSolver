import Debug
import random

class SimplePlusPairPriority:
    def name(self):
        return 'Simple plus pair'
    def guessList(self, solver):
        guessList = []
        self.__two_degree_guess_list(solver, guessList)
        for degree in range(3,10):
            tempGuessList = []
            for i in range(1,10):
                for j in range(1,10):
                    square = solver.puzzle.getSquare(i,j)
                    if square.countRemaining() == degree:
                        for value in square.valuesRemaining():
                            tempGuessList.append((i,j,value))
            if Debug.RANDOMIZE_GUESSLIST:
                random.shuffle(tempGuessList)
            for guess in tempGuessList:
                guessList.append(guess)
        return guessList
    def __two_degree_guess_list(self, solver, guessList):
        degree = 2
        # 9x8/2, 36 possible combinations
        # Do computation piecemeal to enable prioritization
        bitmap_dict = {}
        for i in range(1,10):
            for j in range(1,10):
                square = solver.puzzle.getSquare(i,j)
                if square.countRemaining() == degree:
                    bitmap = square.getBitmap()
                    if bitmap not in bitmap_dict:
                        bitmap_dict[bitmap] = [(i,j)]
                    else:
                        bitmap_dict[bitmap].append((i,j))
        tempGuessList1 = []
        tempGuessList2 = []
        for bitmap in bitmap_dict:
            if len(bitmap_dict[bitmap]) > 1:
                for ijtuple in bitmap_dict[bitmap]:
                    i = ijtuple[0]
                    j = ijtuple[1]
                    square = solver.puzzle.getSquare(i,j)
                    for value in square.valuesRemaining():
                        tempGuessList1.append((i,j,value))
            else:
                ijtuple = bitmap_dict[bitmap][0]
                i = ijtuple[0]
                j = ijtuple[1]
                square = solver.puzzle.getSquare(i,j)
                for value in square.valuesRemaining():
                    tempGuessList2.append((i,j,value))
        if Debug.RANDOMIZE_GUESSLIST:
            random.shuffle(tempGuessList1)
            random.shuffle(tempGuessList2)
        for guess in tempGuessList1:
            guessList.append(guess)
        for guess in tempGuessList2:
            guessList.append(guess)

class SimpleGuessOrderingByTuple:
    def __init__(self, orderingTuple):
        self.orderingTuple = orderingTuple
    def name(self):
        return 'Simple ' + str(self.orderingTuple)
    def guessList(self, solver):
        guessList = []
        for degree in self.orderingTuple:
            singleDegreeGuessList = []
            for i in range(1,10):
                for j in range(1,10):
                    square = solver.puzzle.getSquare(i,j)
                    if square.countRemaining() == degree:
                        for value in square.valuesRemaining():
                            #guessList.append((i,j,value))
                            singleDegreeGuessList.append((i,j,value))
            if Debug.RANDOMIZE_GUESSLIST:
                random.shuffle(singleDegreeGuessList)
            for guess in singleDegreeGuessList:
                guessList.append(guess)
        return guessList
            
