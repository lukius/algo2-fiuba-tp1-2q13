import os
import subprocess

from exception import ProgramCrash


class Program(object):
    
    def __init__(self, binary):
        self.binary = binary
        
    def get_name(self):
        return self.binary
        
    def execute(self, arguments):
        with open(os.devnull, 'w') as devnull:
            arguments_string = arguments.serialize()
            command_list = [self.binary] + arguments_string.split(' ')
            exit_code = subprocess.Popen(command_list, stdout=devnull,
                                         stderr=devnull).wait()
            if exit_code < 0:
                raise ProgramCrash(self.binary, exit_code)
    

class ProgramArguments(object):
    
    def __init__(self):
        self.arguments = dict()
    
    def add(self, key, value=None):
        self.arguments[key] = value
        
    def serialize(self):
        return ' '.join(['%s %s' % (key,value)
                            if value is not None
                            else '%s' % key
                         for (key, value) in self.arguments.items()])
