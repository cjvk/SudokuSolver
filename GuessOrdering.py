import Debug
import random
import hashlib

class GuessOrderingBase:
    def __all_guesses(self, solver):
        guess_list = []
        for i in range(1,10):
            for j in range(1,10):
                square = solver.puzzle.getSquare(i,j)
                if not square.hasSingleValue():
                    for value in square.valuesRemaining():
                        guess_list.append((i,j,value))
        return guess_list
    def _ij_to_box(self, i, j):
        # start in upper left, and "read down the page"
        # 0-indexed
        return (j-1)/3 + ((i-1)/3)*3
    def __ij_position_in_box(self, i, j):
        # i/j are 1-indexed
        # return value is 0-indexed
        i = (i-1) % 3
        j = (j-1) % 3
        return (3*i) + j
    def __comparator_context(self, solver):
        context_dict = {
            'row_degrees_total' : [0] * 9,
            'col_degrees_total' : [0] * 9,
            'box_degrees_total' : [0] * 9,
            'row_degrees_total_twoplus' : [0] * 9,
            'col_degrees_total_twoplus' : [0] * 9,
            'box_degrees_total_twoplus' : [0] * 9,
            'row_degrees_count_twoplus' : [0] * 9,
            'col_degrees_count_twoplus' : [0] * 9,
            'box_degrees_count_twoplus' : [0] * 9,
            'row_bitmap_dupes'  : [set()] * 9,
            'col_bitmap_dupes'  : [set()] * 9,
            'box_bitmap_dupes'  : [set()] * 9,
        }
        row_bitmaps_seen = [set()] * 9
        col_bitmaps_seen = [set()] * 9
        box_bitmaps_seen = [set()] * 9
        for i in range(1,10):
            for j in range(1,10):
                square = solver.puzzle.getSquare(i,j)
                degree = square.countRemaining()
                bitmap = square.getBitmap()
                context_dict[(i,j)] = (degree, bitmap)
                # if seen already, add to dupes
                if bitmap in row_bitmaps_seen[i-1]:
                    context_dict['row_bitmap_dupes'][i-1].add(bitmap)
                row_bitmaps_seen[i-1].add(bitmap)
                if bitmap in col_bitmaps_seen[j-1]:
                    context_dict['col_bitmap_dupes'][j-1].add(bitmap)
                col_bitmaps_seen[j-1].add(bitmap)
                box_number = self._ij_to_box(i,j)
                if bitmap in box_bitmaps_seen[box_number]:
                    context_dict['box_bitmap_dupes'][box_number].add(bitmap)
                box_bitmaps_seen[box_number].add(bitmap)
                # update totals
                context_dict['row_degrees_total'][i-1]+=degree
                context_dict['col_degrees_total'][j-1]+=degree
                context_dict['box_degrees_total'][box_number]+=degree
                # update the "two plus" totals for degree > 1
                if degree != 1:
                    context_dict['row_degrees_total_twoplus'][i-1]+=degree
                    context_dict['row_degrees_count_twoplus'][i-1]+=1
                    context_dict['col_degrees_total_twoplus'][j-1]+=degree
                    context_dict['col_degrees_count_twoplus'][j-1]+=1
                    context_dict['box_degrees_total_twoplus'][box_number]+=degree
                    context_dict['box_degrees_count_twoplus'][box_number]+=1
        return context_dict
    def __random_total_order_comparator(self, item1, item2, random64bits):
        "total ordering, randomized by the supplied 64 bit mask"
        # 4 bits per hex digit (64 bits is 16 hex digits)
        hexdigest1 = hashlib.sha224(str(item1)).hexdigest()[0:16]
        hexdigest2 = hashlib.sha224(str(item2)).hexdigest()[0:16]
        hash1 = int(hexdigest1, 16)
        hash2 = int(hexdigest2, 16)
        randomized_hash1 = hash1 ^ random64bits
        randomized_hash2 = hash2 ^ random64bits
        if randomized_hash1 < randomized_hash2:
            return -1
        if randomized_hash1 > randomized_hash2:
            return 1
        return 0
    def guessList(self, solver):
        all_guesses = self.__all_guesses(solver)
        comparator_context = self.__comparator_context(solver)
        random64bits = random.getrandbits(64) # returns a long
        def comparator(item1, item2):
            sort_response = self.primary_comparator(item1, item2, comparator_context)
            if sort_response != 0:
                return sort_response
            return self.__random_total_order_comparator(item1, item2, random64bits)
        all_guesses.sort(cmp=comparator)
        return all_guesses

class SimplePlusPairPriority2 (GuessOrderingBase):
    def name(self):
        return 'Simple_plus_pair2'
    def primary_comparator(self, item1, item2, context):
        # setup
        ij1, ij2 = item1[0:2], item2[0:2]
        i1, j1, i2, j2 = ij1[0], ij1[1], ij2[0], ij2[1]
        item1degree, item2degree = context[ij1][0], context[ij2][0]
        item1bitmap, item2bitmap = context[ij1][1], context[ij2][1]
        item1boxnum, item2boxnum = self._ij_to_box(i1,j1), self._ij_to_box(i2,j2)

        # sort 1: node degree
        if item1degree != item2degree:
            return item1degree - item2degree

        # sort 2: (2 degree nodes only) prioritize duplicates
        if item1degree is 2:
            item1dupcount = 0
            if item1bitmap in context['row_bitmap_dupes'][i1-1]:
                item1dupcount += 1
            if item1bitmap in context['col_bitmap_dupes'][j1-1]:
                item1dupcount += 1
            if item1bitmap in context['box_bitmap_dupes'][item1boxnum]:
                item1dupcount += 1
            item2dupcount = 0
            if item2bitmap in context['row_bitmap_dupes'][i2-1]:
                item2dupcount += 1
            if item2bitmap in context['col_bitmap_dupes'][j2-1]:
                item2dupcount += 1
            if item2bitmap in context['box_bitmap_dupes'][item2boxnum]:
                item2dupcount += 1
            if item1dupcount != item2dupcount:
                return item1dupcount - item2dupcount
        return 0

class DegreeRowColBoxDegree2 (GuessOrderingBase):
    def name(self):
        return 'DegreeRowColBoxDegree2'
    def primary_comparator(self, item1, item2, context):
        # setup
        ij1, ij2 = item1[0:2], item2[0:2]
        i1, j1, i2, j2 = ij1[0], ij1[1], ij2[0], ij2[1]
        item1degree, item2degree = context[ij1][0], context[ij2][0]
        item1bitmap, item2bitmap = context[ij1][1], context[ij2][1]
        item1boxnum, item2boxnum = self._ij_to_box(i1,j1), self._ij_to_box(i2,j2)

        # sort 1: node degree
        if item1degree != item2degree:
            return item1degree - item2degree

        # sort 2: min total degree of row/col/box
        item1mindegree = min(
            context['row_degrees_total'][i1-1],
            context['col_degrees_total'][j1-1],
            context['row_degrees_total'][item1boxnum],
        )
        item2mindegree = min(
            context['row_degrees_total'][i2-1],
            context['col_degrees_total'][j2-1],
            context['row_degrees_total'][item2boxnum],
        )
        if item1mindegree != item2mindegree:
            return item1mindegree - item2mindegree

        return 0

class SimpleGuessOrderingByTuple2(GuessOrderingBase):
    def __init__(self, orderingTuple):
        self.orderingTuple = orderingTuple
    def name(self):
        return 'Simple2 ' + str(self.orderingTuple)
    def primary_comparator(self, item1, item2, context):
        # setup
        ij1, ij2 = item1[0:2], item2[0:2]
        item1degree, item2degree = context[ij1][0], context[ij2][0]

        # sort: position of node degree in orderingTuple
        item1pos = self.orderingTuple.index(item1degree)
        item2pos = self.orderingTuple.index(item2degree)
        if item1pos != item2pos:
            return item1pos - item2pos

        return 0

############################################################
#
#                Below this: Archive
#
############################################################

class SimplePlusPairPriority:
    """
    sort 1: node degree
    sort 2: (2 degree only) prioritize pairs
    """
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

        print 'guess ordering debugging: begin'
        solver.puzzle.printPuzzle()
        print '--------------- 1'
        for i in range(1,10):
            for j in range(1,10):
                sq = solver.puzzle.getSquare(i,j)
                t = (i,j,str(sq.valuesRemaining()))
                print 'i/j/valuesremaining = %d/%d/%s' % t
        print '--------------- 2'
        print guessListList
        print 'guess ordering debugging: end'
        exit()

        return self.__combine_guess_lists(guessListList)

class DegreeRowColBoxDegree2_deprecated:
    def name(self):
        return 'DegreeRowColBoxDegree2'
    def __ij_to_box(self, i, j):
        # start in upper left, and "read down the page"
        # 0-indexed
        return (j-1)/3 + ((i-1)/3)*3
    def all_guesses(self, solver):
        guess_list = []
        for i in range(1,10):
            for j in range(1,10):
                square = solver.puzzle.getSquare(i,j)
                if not square.hasSingleValue():
                    for value in square.valuesRemaining():
                        guess_list.append((i,j,value))
        return guess_list
    def __comparator_context(self, solver):
        context_dict = {
            'row_degrees_total' : [0] * 9,
            'col_degrees_total' : [0] * 9,
            'box_degrees_total' : [0] * 9,
            'row_degrees_count' : [0] * 9,
            'col_degrees_count' : [0] * 9,
            'box_degrees_count' : [0] * 9,
        }
        for i in range(1,10):
            for j in range(1,10):
                square = solver.puzzle.getSquare(i,j)
                degree = square.countRemaining()
                #context_dict[(i,j)] = (square, degree)
                context_dict[(i,j)] = degree
                # update the totals for degree > 1
                if degree != 1:
                    context_dict['row_degrees_total'][i-1]+=degree
                    context_dict['row_degrees_count'][i-1]+=1
                    context_dict['col_degrees_total'][j-1]+=degree
                    context_dict['col_degrees_count'][j-1]+=1
                    box_number = self.__ij_to_box(i,j)
                    context_dict['box_degrees_total'][box_number]+=degree
                    context_dict['box_degrees_count'][box_number]+=1
        return context_dict
    def __comparator(self, item1, item2, context, bitmask):
        # '<' or '<=' are examples
        # item1 and item2 are tuples of the form (i, j, value)

        # setup
        ij1 = item1[0:2]
        ij2 = item2[0:2]
        i1 = ij1[0]
        j1 = ij1[1]
        i2 = ij2[0]
        j2 = ij2[1]

        # sort 1: node degree
        if context[ij1] != context[ij2]:
            return context[ij1] - context[ij2]

        # sort 2: min(row/col/box)
        box1 = self.__ij_to_box(i1,j1)
        box2 = self.__ij_to_box(i2,j2)
        # value1 = min(
        #     float(context['row_degrees_total'][i1-1])/context['row_degrees_count'][i1-1],
        #     float(context['col_degrees_total'][j1-1])/context['col_degrees_count'][j1-1],
        #     float(context['box_degrees_total'][box1])/context['box_degrees_count'][box1]
        # )
        # value2 = min(
        #     float(context['row_degrees_total'][i2-1])/context['row_degrees_count'][i2-1],
        #     float(context['col_degrees_total'][j2-1])/context['col_degrees_count'][j2-1],
        #     float(context['box_degrees_total'][box2])/context['box_degrees_count'][box2]
        # )
        value1 = context['row_degrees_total'][i1-1]
        value1+= context['col_degrees_total'][j1-1]
        value1+= context['box_degrees_total'][box1]
        value2 = context['row_degrees_total'][i2-1]
        value2+= context['col_degrees_total'][j2-1]
        value2+= context['box_degrees_total'][box2]
        # if value1 != value2:
        #     if value1 < value2:
        #         return -1
        #     else:
        #         return 1

        # sort 3: random, nondeterministic, AND totally ordered
        #hash1 = hash(item1)
        #hash2 = hash(item2)
        # 4 bits per hex digit
        # 64 bits is 16 hex digits
        hexdigest1 = hashlib.sha224(str(item1)).hexdigest()[0:16]
        hexdigest2 = hashlib.sha224(str(item2)).hexdigest()[0:16]
        hash1 = int(hexdigest1, 16)
        hash2 = int(hexdigest2, 16)
        # here is the nondeterministic part
        ndhash1 = hash1 ^ bitmask
        ndhash2 = hash2 ^ bitmask
        if ndhash1 < ndhash2:
            return -1
        if ndhash1 > ndhash2:
            return 1
        return 0

        # sort 4: simple compare (to debug)
        for pos in (0,1,2):
            if item1[pos] != item2[pos]:
                return item1[pos] - item2[pos]
        return 0
    def guessList(self, solver):
        # sort 1: node degree
        # sort 2: min(row/col/box)
        # sort 3: random AND totally ordered
        all_guesses = self.all_guesses(solver)
        comparator_context = self.__comparator_context(solver)

        # create the comparator for sorting
        random64bits = random.getrandbits(64) # long
        def comparator(item1, item2):
            return self.__comparator(item1, item2, comparator_context, random64bits)

        all_guesses.sort(cmp=comparator)

        # print 'guess ordering debugging: begin'
        # solver.puzzle.printPuzzle()
        # print '--------------- 1'
        # for i in range(1,10):
        #     for j in range(1,10):
        #         sq = solver.puzzle.getSquare(i,j)
        #         t = (i,j,str(sq.valuesRemaining()))
        #         print 'i/j/valuesremaining = %d/%d/%s' % t
        # print '--------------- 2'
        # print comparator_context
        # print '--------------- 3'
        # print all_guesses
        # print 'guess ordering debugging: end'
        # exit()

        return all_guesses

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
            
class NoGuesses:
    def name(self):
        return 'No guesses, no search'
    def guessList(self, solver):
        guessList = []
        return guessList
