#!/usr/bin/python

# Sudoku Solver

from Puzzle import SudokuPuzzle
import Solver
import SamplePuzzles
import time
import Profiler
import GuessOrdering
import Debug
import sys
import hashlib

PUZZLES = (
    SamplePuzzles.getById('from_a_20200126_testing'),
    #SamplePuzzles.getById('from_a_20200126'),
    #SamplePuzzles.getById('sjm20190118'),
    #SamplePuzzles.getById('sjm20160310'),
    #SamplePuzzles.getById('worldshardest'),
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

def profileStrategy():
    Debug.DEBUG = 0

    strategies = (
        GuessOrdering.SimpleGuessOrderingByTuple2(range(2,10)),
        #GuessOrdering.SimpleGuessOrderingByTuple2((6,5,4,3,2,7,8,9)),
        #GuessOrdering.SimplePlusPairPriority2(),
        #GuessOrdering.DegreeRowColBoxDegree2(),
        #GuessOrdering.DegreeRowColBoxDegree(True),
        #GuessOrdering.DegreeRowColBoxDegree(),
        #GuessOrdering.SimplePlusPairPriority(),
        #GuessOrdering.SimpleGuessOrderingByTuple(range(2,10)),
        #GuessOrdering.SimpleGuessOrderingByTuple((3,2,4,5,6,7,8,9)),
        #GuessOrdering.SimpleGuessOrderingByTuple((4,3,2,5,6,7,8,9)),
        #GuessOrdering.SimpleGuessOrderingByTuple((9,8,7,6,5,4,3,2)),
        #GuessOrdering.SimpleGuessOrderingByTuple((5,4,3,2,6,7,8,9)),
        #GuessOrdering.SimpleGuessOrderingByTuple((6,5,4,3,2,7,8,9)),
        #GuessOrdering.SimpleGuessOrderingByTuple((7,6,5,4,3,2,8,9)),
        #GuessOrdering.SimpleGuessOrderingByTuple((5,4,2,3,6,7,8,9)),
        #GuessOrdering.SimpleGuessOrderingByTuple((5,2,3,4,6,7,8,9)),
    )

    uberresults = []
    number_of_trials = 10

    for i in range(0, len(strategies)):
        strategy = strategies[i]
        trial_results = []
        sum = [0, 0]

        for trial in range(0, number_of_trials):
            Profiler.STOPWATCHES = {}
            Solver.TOTAL_GUESSES_MADE = 0
            p = SudokuPuzzle(SamplePuzzles.getById('worldshardest').getPuzzle())
            s = Solver.Solver(p, strategy)
            Profiler.startStopWatch('cjvk')
            s.solve()
            sys.stdout.write('.')
            sys.stdout.flush()
            Profiler.stopStopWatch('cjvk')
            total_elapsed_time = Profiler.STOPWATCHES['cjvk'].totalElapsed
            trial_results.append((Solver.TOTAL_GUESSES_MADE, total_elapsed_time))
            sum[0] += Solver.TOTAL_GUESSES_MADE
            sum[1] += total_elapsed_time

        name = strategy.name()
        nps = sum[0]/sum[1]
        avg_time = sum[1]/number_of_trials
        avg_guesses = sum[0]/number_of_trials
        ubertuple = (name, nps, avg_time, avg_guesses)

        uberresults.append(ubertuple)
        whichone = str(i+1) + '/' + str(len(strategies))
        #sys.stdout.write(str(len(strategies)-i) + '\n')
        sys.stdout.write(' ' + whichone + '     ' + str(ubertuple) + '\n')
        sys.stdout.flush()
    
    print 'name, number_of_trials, nps, avg_time, avg_guesses'
    for uberresult in uberresults:
        name = str(uberresult[0])
        nps = uberresult[1]
        avg_time = uberresult[2]
        avg_guesses = uberresult[3]
        print 'name=', name
        print 'number_of_trials=', number_of_trials
        print 'nps=', nps
        print 'avg_time=', avg_time
        print 'avg_guesses=', avg_guesses
        #print name, number_of_trials, nps, avg_time, avg_guesses

def runOnePuzzle(orderingStrategy):
    for puzzle in PUZZLES:
        p = SudokuPuzzle(puzzle.getPuzzle())
        Debug.debug(puzzle.getName(),1)
        Debug.debugPrintPuzzle(p, 1)
        s = Solver.Solver(p, orderingStrategy)
        time_start = time.time()
        s.solve()
        time_end = time.time()
        elapsed_time = time_end - time_start
        Profiler.printAll(elapsed_time)
        print 'solved puzzle'
        print 'name:', puzzle.getName()
        p.printPuzzle()
        pass
    pass

def runOnePuzzleWithSearch():
    runOnePuzzle(GuessOrdering.SimpleGuessOrderingByTuple((4,3,2,5,6,7,8,9)))

def runOnePuzzleWithoutSearch():
    runOnePuzzle(GuessOrdering.NoGuesses())

MODES = {
    '1' : {'f' : runOnePuzzleWithSearch},
    '2' : {'f' : runOnePuzzleWithoutSearch},
    '3' : {'f' : profileStrategy},
    }

def main():
    print 'Welcome to SudokuSolver! Please make mode selection'
    puzzle_name = PUZZLES[0].getName()
    print ''
    print 'selected sudoku: ' + puzzle_name
    print '  1) solve sudoku'
    print '  2) run solver with search disabled'
    print '  3) run profiler against "World\'s hardest Sudoku"'
    choice = raw_input()
    if choice not in MODES.keys():
        print 'did not understand ' + str(choice) + ', exiting'
        exit()

    f = MODES[choice]['f']

    f()
    pass

main()
