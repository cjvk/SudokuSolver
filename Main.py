#!/usr/bin/python

# Sudoku Solver

from Puzzle import SudokuPuzzle
from Solver import Solver
import SamplePuzzles

PUZZLES = (
    SamplePuzzles.getById('worldshardest'),
    #SamplePuzzles.getById('sjm20160304'),
    #SamplePuzzles.getById('7sudokuvd1'),
    #SamplePuzzles.getById('ss20160302h'),
    #SamplePuzzles.getById('ss20160303h'),
    #SamplePuzzles.getById('ss20160301e'),
    #SamplePuzzles.getById('ss20160302e'),
    #SamplePuzzles.getById('test1', SamplePuzzles.TEST_PUZZLES),
    #SamplePuzzles.getById('sjm20160229'),
    #SamplePuzzles.getById('sjm20160302'),
)
for puzzle in PUZZLES:
    p = SudokuPuzzle(puzzle.getPuzzle())
    print puzzle.getName()
    p.printPuzzle()
    s = Solver(p)
    s.solve()
    print 'solved puzzle'
    print 'name:', puzzle.getName()
    p.printPuzzle()

exit()
