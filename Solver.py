import time
import Constraints

class QueueItem:
    def __init__(self, row, column):
        if row < 1 or row > 9 or column < 1 or column > 9:
            raise ValueError('Sudoku only works 1-9');
        self.row = row
        self.column = column

class Solver:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.queue = []
        self.constraintQueue = []
        self.constraintQueue.append(Constraints.NoRowDuplicates(self.puzzle))
        self.constraintQueue.append(Constraints.NoColumnDuplicates(self.puzzle))
        self.constraintQueue.append(Constraints.NoBoxDuplicates(self.puzzle))
        self.constraintQueue.append(Constraints.ProcessOfElimination(self.puzzle))
        
    def process(self, queueItem):
        for constraint in self.constraintQueue:
            constraint.process(queueItem)
        pass

    def solve(self):
        """
        1) enqueue all InitialSquare objects
        2) clean all squares
        3) if queue empty, exit; otherwise
           a. run through queue completely
           b. check if done
           c. enqueue any square which is dirty (and clean square)
           d. go to 3)
        """
        print 'solving...'
        time_start = time.time()
        # enqueue all InitialSquare objects
        for i in range(1,10):
            for j in range(1,10):
                if self.puzzle.getSquare(i,j).hasSingleValue():
                    queueItem = QueueItem(i,j)
                    self.enqueue(queueItem)
        # clean all squares
        self.cleanAll()
        print 'queue length:' + str(len(self.queue))
        MAX_RUNS = 30
        for run in range(0, MAX_RUNS):
            print 'run ' + str(run) + ': queue length = ' + str(len(self.queue))
            if len(self.queue) == 0:
                print 'queue zero length, exiting on ' + str(run) + 'th run'
                break
            # run through queue completely
            while len(self.queue) > 0:
                queueItem = self.queue.pop()
                self.process(queueItem)
            if self.doneYet():
                print 'done!'
                break
            for i in range(1,10):
                for j in range(1,10):
                    if self.puzzle.getSquare(i,j).isDirty():
                        queueItem = QueueItem(i,j)
                        self.enqueue(queueItem)
                        self.puzzle.getSquare(i,j).clean()
        time_end = time.time()
        print 'solving finished, elapsed time = ' + str(time_end-time_start)
    def cleanAll(self):
        for i in range(1,10):
            for j in range(1,10):
                self.puzzle.getSquare(i,j).clean()
    def enqueue(self, queueItem):
        self.queue.append(queueItem)
    def doneYet(self):
        for i in range(1,10):
            for j in range(1,10):
                if not self.puzzle.getSquare(i,j).hasSingleValue():
                    return False
        return True
    pass
