from abc import ABC, abstractmethod


class TwoStepVerificationAbstractClass(ABC):

    '''
     Parameters: array possible_values
     Returns: string
     '''
    @abstractmethod
    def getVerificationType(self, possible_values):
        pass

    '''
     Returns: string
     '''
    @abstractmethod
    def getSecurityCode(self):
        pass
