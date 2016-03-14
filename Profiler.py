import time

STOPWATCHES = { }

def startStopWatch(name):
    if name not in STOPWATCHES:
        STOPWATCHES[name] = StopWatch()
    STOPWATCHES[name].start()
def stopStopWatch(name):
    STOPWATCHES[name].stop()
def printAll(elapsedTime = None):
    if not elapsedTime is None:
        print 'Profiling info: total elapsed time=%f' % (elapsedTime,)
    else:
        print 'Profiling info:'
    allNames = []
    for name in STOPWATCHES:
        allNames.append(name)
    allNames.sort()
    for name in allNames:
        value = STOPWATCHES[name].totalElapsed
        if not elapsedTime is None:
            percentOfTotal = (value / elapsedTime) * 100
            print 'total time for {}: {:f} ({:f}% of total)'.format(
                name, value, percentOfTotal)
        else:
            print 'total time for {}: {:f}'.format(name, value)

class StopWatch:
    def __init__(self):
        self.running = False
        self.totalElapsed = 0.0
        self.time_start = None
    def start(self):
        if self.running:
            raise ValueError('cannot start a running stopwatch')
        self.time_start = time.time()
        self.running = True
    def stop(self):
        if not self.running:
            raise ValueError('cannot stop a stopped stopwatch')
        time_end = time.time()
        self.running = False
        self.totalElapsed += (time_end - self.time_start)
        self.time_start = None
    pass

