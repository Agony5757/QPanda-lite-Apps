from scipy.optimize import curve_fit, OptimizeWarning
import warnings
import numpy as np
from random import choice
from collections import Counter
import matplotlib.pyplot as plt 
import logging

COLORS = [
    "tab:blue", 
    "tab:orange", 
    "tab:green", 
    "tab:red", 
    "tab:purple", 
    "tab:cyan", 
    "tab:brown", 
    "tab:pink", 
    "tab:gray", 
    "tab:olive"
    ]

class TermData:
    """This class stores the expectation values collected at different depths for a single
    Pauli in the sparse model. It handles fitting a fidelitiy and SPAM coefficients to this
    expectation value as well as storing and interpreting the results of degeneracy-lifting measurements"""

    def __init__(self, pauli, pair):
        self.pauli = pauli #pauli term
        self.pair = pair #conjugate by clifford layer

        self._expectations = {} #expectations at different depths
        self._count = Counter() #counts at different depths

        self._single_vals = [] #degeneracy-lifting single-depth measurements
        self._single_count = 0 #number of single-depth measurements
        self.single_fidelity = None

        self._spam = None #spam coefficients
        self._fidelity = None #fidelity
        self.pair_fidelity = None

    
    def add_expectation(self, depth, expectation):
        """Add the value of a measurement to the term data"""
        self._expectations[depth] = self._expectations.get(depth, 0) + expectation
        self._count[depth] = self._count.get(depth, 0) + 1
            

    def depths(self):
        """Return the measurement depths as a list in increasing order"""

        return list(sorted(self._expectations.keys()))

    def expectations(self):
        """Return the expectation values measured corresponding to the different depths
        in increasing order"""

        return [self._expectations[d]/self._count[d] for d in self.depths()]

    def _fit(self):
        expfit = lambda x,a,b: a*np.exp(-b*x) #Decay of twirled channel is exponential
        try: #OptimizeWarning will be caught by filter
            #print('depths:{},expectations:{}'.format(self.depths(),self.expectations()))
            (a,b),_ = curve_fit(expfit, self.depths(), self.expectations(), p0 = [.8, .1], bounds = ((0,0),(1,1)))           
            #(a,b),_ = curve_fit(expfit, self.depths(), self.expectations())
        except:
            (a,b) = 1,0
            print("Fit did not converge!")
        return a,b


    def fit(self):
        """Fit the fidelity curve to an exponential decay and store the fidelity and spam
        parameters"""

        #perform fit of pair
        a,b = self._fit()
        self.spam = a
        self.pair_fidelity = np.exp(-b)
        self.fidelity = np.exp(-b)

    def graph(self,path,qubit_list):
        """Graph the fidelity of the Pauli at different depths vs the exponential fit"""

        c = choice(COLORS)
        axis = np.linspace(0,max(self.depths()), 100)
        a,b = self._fit()
        plt.plot(self.depths(), self.expectations(), color = c,  linestyle = 'None', marker = 'x')
        plt.plot(axis, [a*np.exp(-b*x) for x in axis], color = c)
        plt.title("Qubit {}\nbase {}, a = {}, b= {} ".format(qubit_list, self.pauli,a,np.exp(-b)))
        plt.savefig(path)
        plt.close()