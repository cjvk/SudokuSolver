#!/usr/bin/python

# Sudoku Solver

from Puzzle import SudokuPuzzle
from Solver import Solver
import SamplePuzzles

puzzle2 = SudokuPuzzle(SamplePuzzles.NEWSPAPER_PUZZLE_02_29_2016)
puzzle2.printPuzzle()
s2 = Solver(puzzle2)
s2.solve()
print 'solved puzzle'
puzzle2.printPuzzle()

exit()
