"""Component Model

Component Model Base Class
"""

# Imports
import sys
sys.path.append("../hardware/")
from HardwareComm import HardwareComm

# Component model base class
class ComponentModel():
  def __init__(self, name, hardwareComm, modelLock):
    """ComponentModel base class constructor"""
    self.type = self.__class__.__name__
    self.name = name
    self.hardwareComm = hardwareComm
    self.modelLock = modelLock

  def protectedReturn1(self, pGetFunction):
    """Returns the value of the variable as protected by the model lock"""
    self.modelLock.acquire()
    pReturn1 = pGetFunction(self, False)
    self.modelLock.release()
    return pReturn1

  def protectedReturn2(self, pVariable1, pVariable2):
    """Returns the value of the variables as protected by the model lock"""
    self.modelLock.acquire()
    pReturn1, pReturn2 = pGetFunction(self, False)
    self.modelLock.release()
    return pReturn1, pReturn2

  def protectedReturn3(self, pVariable1, pVariable2, pVariable3, bLockModel):
    """Returns the value of the variables as protected by the model lock"""
    self.modelLock.acquire()
    pReturn1, pReturn2, pReturn3 = pGetFunction(self, False)
    self.modelLock.release()
    return pReturn1, pReturn2, pReturn3
