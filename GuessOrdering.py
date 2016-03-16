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

class DegreeRowColBoxDegree:
    def __init__(self, invert_subsort = False):
        self.ordering_tuple = range(2,10)
        self.invert_subsort = invert_subsort
    def name(self):
        if not self.invert_subsort:
            return 'DegreeRowColBoxDegree'
        else:
            return 'DegreeRowColBoxDegreeInverted'
    def __ij_to_box(self, i, j):
        # start in upper left, and "read down the page"
        # 0-indexed
        return (j-1)/3 + ((i-1)/3)*3
    def __combine_guess_lists(self, list_of_lists):
        guessList = []
        for single_list in list_of_lists:
            if Debug.RANDOMIZE_GUESSLIST:
                random.shuffle(single_list)
            for guess in single_list:
                guessList.append(guess)
        return guessList
    def guessList(self, solver):
        # first, sort by degree of square
        # next, sort by min total degree of row/col/box
        # I know the possible degrees of squares
        # I do not know the possible total degrees

        row_degrees = [0] * 9
        col_degrees = [0] * 9
        box_degrees = [0] * 9
        squares_by_degree = {}
        for degree in range(2,10):
            squares_by_degree[degree] = []
        for i in range(1,10):
            for j in range(1,10):
                square = solver.puzzle.getSquare(i,j)
                degree = square.countRemaining()
                row_degrees[i-1]+=degree
                col_degrees[j-1]+=degree
                box_degrees[self.__ij_to_box(i,j)]+=degree
                if degree > 1:
                    squares_by_degree[degree].append((i,j))

        guessListList = []
        for degree in self.ordering_tuple:
            min_degree_dict = {}
            for ijtuple in squares_by_degree[degree]:
                i = ijtuple[0]
                j = ijtuple[1]
                rd = row_degrees[i-1]
                cd = col_degrees[j-1]
                bd = box_degrees[self.__ij_to_box(i,j)]
                mindegree = min(rd, cd, bd)
                if mindegree not in min_degree_dict:
                    min_degree_dict[mindegree] = []
                min_degree_dict[mindegree].append(ijtuple)
            all_possible_min_degrees = min_degree_dict.keys()
            all_possible_min_degrees.sort(reverse=self.invert_subsort)
            for mindegree in all_possible_min_degrees:
                guessListForThisLevel = []
                for ijtuple in min_degree_dict[mindegree]:
                    i = ijtuple[0]
                    j = ijtuple[1]
                    square = solver.puzzle.getSquare(i,j)
                    for value in square.valuesRemaining():
                        guessListForThisLevel.append((i,j,value))
                guessListList.append(guessListForThisLevel)

        return self.__combine_guess_lists(guessListList)

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
            
