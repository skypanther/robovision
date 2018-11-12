'''
Abstract base class (aka 'interface') for video interfaces
'''
import abc


class AbstractCam(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def open(self):
        raise NotImplementedError('You must define an open method')

    @abc.abstractmethod
    def close(self):
        raise NotImplementedError('You must define a close method')

    @abc.abstractmethod
    def read_frame(self):
        raise NotImplementedError('You must define a read_frame method')
