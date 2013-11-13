# -*- coding: utf-8 -*- 

class GameException(Exception):
    
    def get_army_name(self):
        return self.army_name
    
    def set_army_name(self, army_name):
        self.army_name = army_name    


class ValidationException(GameException):
    
    def __init__(self, rule):
        self.rule = rule
        self.army_name = rule.get_object().get_soldier().get_army_name()
    
    def __str__(self):
        army_name = self.rule.get_object().get_soldier().get_army_name()
        string = '%s violó las reglas de validación!\n%s'
        return string % (army_name, str(self.rule))
    

class ParsingException(GameException):

    def __init__(self, text):
        self.text = text
        
    def __str__(self):
        program_name = self.program.get_name()
        return '%s: formato de salida incorrecto (%s)' % (program_name,
                                                          self.text.strip())
    
    
class MissingFileException(GameException):
    
    def __init__(self, army_name, program, input_filename):
        self.army_name = army_name
        self.program = program
        self.input_filename = input_filename

    def __str__(self):
        string = 'archivo de salida inexistente al ejecutar ' +\
                 '%s -i %s -o <salida>!'
        program_name = self.program.get_name()
        return string % (program_name, self.input_filename)

        
class ProgramCrash(GameException):

    def __init__(self, program, exit_code):
        self.program = program
        self.exit_code = exit_code

    def __str__(self):
        string = '%s crasheó! (exit code: %d)'
        return string % (self.program, self.exit_code)
    
    
class WebBrowsersMissingException(Exception):
    
    def __init__(self, browsers):
        self.browsers = browsers
        
    def __str__(self):
        browsers = ', '.join(self.browsers)
        string = 'no se encontró ningún navegador soportado (%s)' % browsers
        return string