import random

class PuzzleDescription:
    def __init__(self, id, name, puzzle):
        self.__id = id
        self.__name = name
        self.validate(puzzle)
        self.__puzzle = puzzle
    def validate(self, puzzle):
        for line in puzzle:
            if not len(line) == 9:
                raise ValueError('Sudoku validation error')
            for index in range(0,9):
                char = line[index]
                if char != ' ':
                    digit = int(char)
                    if digit < 1 or digit > 9:
                        raise ValueError('Sudoku validation error, digit=' + str(digit))
    def getId(self):
        return self.__id
    def getName(self):
        return self.__name
    def getPuzzle(self):
        return self.__puzzle
    def toString(self):
        s = "name: " + str(self.getName())
        for line in self.getPuzzle():
            s += "\n"
            s += line
        return s
    pass

# http://www.sudokusaviour.com/

SAMPLE_PUZZLES = (
    PuzzleDescription(
        id='worldshardest',
        name='http://www.telegraph.co.uk/news/science/science-news/9359579/Worlds-hardest-sudoku-can-you-crack-it.html',
        puzzle=(
            '8        ',
            '  36     ',
            ' 7  9 2  ',
            ' 5   7   ',
            '    457  ',
            '   1   3 ',
            '  1    68',
            '  85   1 ',
            ' 9    4  ',
        )
    ),
    PuzzleDescription(
        id='7sudokuvd1',
        name='http://www.7sudoku.com/very-difficult, topleft',
        puzzle=(
            '2     63 ',
            ' 1   3   ',
            '  5  7  9',
            ' 4 7   6 ',
            '  38 91  ',
            ' 2   5 4 ',
            '1  9  4  ',
            '   5   9 ',
            ' 56     7',
        )
    ),
    PuzzleDescription(
        id='ss20160302h',
        name='sudokusaviour, 3/2/2016, hard',
        puzzle=(
            '  92    5',
            '  4 8   7',
            '7    34  ',
            ' 3  9 12 ',
            '   5 1   ',
            ' 48 6  5 ',
            '  14    3',
            '4   5 9  ',
            '6    85  ',
        )
    ),
    PuzzleDescription(
        id='ss20160303h',
        name='sudokusaviour, 3/3/2016, hard',
        puzzle=(
            ' 9   5 27',
            '         ',
            ' 439  8  ',
            '5 84  26 ',
            '   5 3   ',
            ' 24  65 9',
            '  5  194 ',
            '         ',
            '41 2   5 ',
        )
    ),
    PuzzleDescription(
        id='ss20160301e',
        name='sudokusaviour, 3/1/2016, easy',
        puzzle=(
            '     6258',
            '    7 1  ',
            '  5 4   9',
            '   4    3',
            '5 6 8 7 1',
            '9    7   ',
            '8   9 4  ',
            '  2 5    ',
            '7692     ',
        )
    ),
    PuzzleDescription(
        id='ss20160302e',
        name='sudokusaviour, 3/2/2016, easy',
        puzzle=(
            '1 26 7   ',
            ' 739 4   ',
            '4   3    ',
            ' 19      ',
            '3 4   6 9',
            '      28 ',
            '    9   1',
            '   2 637 ',
            '   1 39 6',
        )
    ),
    PuzzleDescription(
        id='sjm20160302',
        name='Mercury News, 3/2/2016, difficulty: 2/4',
        puzzle=(
            '    3    ',
            '  6  58 2',
            '9    7   ',
            ' 2   1  9',
            ' 3  5  2 ',
            '7  6   3 ',
            '   9    1',
            '  251 6 8',
            '    4    ',
        )
    ),
    PuzzleDescription(
        id='sjm20160229',
        name='Mercury News, 2/29/2016, difficulty: 1/4',
        puzzle=(
            '3  2    4',
            '   5 37  ',
            '    6 5  ',
            ' 12  93  ',
            '   182   ',
            '  67  18 ',
            '  8 9    ',
            '  93 1   ',
            '5    7  6',
        )
    ),
)

TEST_PUZZLES = (
    PuzzleDescription(
        id='test1',
        name='completely solved puzzle (corner case)',
        puzzle=(
            '946287351',
            '583619742',
            '217543698',
            '865432179',
            '721965483',
            '439178526',
            '678324915',
            '394851267',
            '152796834',
        )
    ),
    PuzzleDescription(
        id='test2',
        name='nearly solved puzzle (1 away in all rows)',
        puzzle=(
            '94628735 ',
            '5836 9742',
            '2 7543698',
            '865432 79',
            '72 965483',
            '439 78526',
            '6783249 5',
            '39485 267',
            ' 52796834',
        )
    ),
)

def getById(id, puzzleList=SAMPLE_PUZZLES):
    for puzzle in puzzleList:
        if puzzle.getId() == id:
            return puzzle
    return None

def getRandomPuzzle(puzzleList=SAMPLE_PUZZLES):
    return random.choice(puzzleList)

