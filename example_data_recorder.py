import numpy as np
import time

class RobotDataRecorder:
    def __init__(self, r, max_iterations):
        # Preallocate arrays based on the expected number of iterations
        self.max_iterations = max_iterations
        self.it = 0

        self.trun = np.zeros(max_iterations)
        self.tt = np.zeros(max_iterations)
        self.qt = np.zeros((max_iterations, len(r._actual.q)))  
        self.qdt = np.zeros((max_iterations, len(r._actual.qdot)))
        self.rqt = np.zeros((max_iterations, len(r._command.q)))
        self.rqdt = np.zeros((max_iterations, len(r._command.qdot)))
        self.xt = np.zeros((max_iterations, len(r._actual.x))) 
        self.vt = np.zeros((max_iterations, len(r._actual.v)))
        self.rxt = np.zeros((max_iterations, len(r._command.x)))
        self.rvt = np.zeros((max_iterations, len(r._command.v)))
    
    def record_callback(self, r):
        # Check if we've exceeded the pre-allocated size
        if self.it >= self.max_iterations:
            raise IndexError("Exceeded max iterations")
        
        # Collect data in the preallocated arrays
        self.trun[self.it] = time.monotonic()
        self.tt[self.it] = r.Time
        self.qt[self.it] = r._actual.q
        self.qdt[self.it] = r._actual.qdot
        self.rqt[self.it] = r._command.q
        self.rqdt[self.it] = r._command.qdot
        self.xt[self.it] = r._actual.x
        self.vt[self.it] = r._actual.v
        self.rxt[self.it] = r._command.x
        self.rvt[self.it] = r._command.v

        # Increment the iteration counter
        self.it += 1