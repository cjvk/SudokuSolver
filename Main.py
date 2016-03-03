#!/usr/bin/python

# Sudoku Solver

from Puzzle import SudokuPuzzle
from Solver import Solver
import SamplePuzzles

PUZZLES = (
    #SamplePuzzles.getById('test1', SamplePuzzles.TEST_PUZZLES),
    #SamplePuzzles.getById('sjm20160229'),
    #SamplePuzzles.getById('sjm20160302'),
    SamplePuzzles.getById('ss20160302e'),
)

for puzzle in PUZZLES:
    p = SudokuPuzzle(puzzle.getPuzzle())
    print puzzle.getName()
    p.printPuzzle()
    s = Solver(p)
    s.solve()
    print 'solved puzzle'
    p.printPuzzle()

exit()
