# -*- coding: utf-8 -*- 

import logging

from argparse import ArgumentParser

from exception import GameException
from manager import GameManager


class Main(object):
    
    DESCRIPTION = 'Juez de batalla -- Algoritmos II'
    HELP_REPLAY = 'Intentar repetir la batalla (si existiese) en lugar de\
                   simularla nuevamente'
    HELP_TEXT = 'Utilizar sólo texto plano para mostrar los resultados de\
                 la simulación (no usa gráficos)'
    HELP_MESSAGE = 'Mostrar ayuda y salir'
    
    def __init__(self):
        logging_level = logging.DEBUG
        logging.basicConfig(format='%(levelname)s: %(message)s',
                            level=logging_level)
    
    def parse_cmdline(self):
        parser = ArgumentParser(description=self.DESCRIPTION,
                                add_help=False)
        
        positionals = parser.add_argument_group('Argumentos posicionales')
        positionals.add_argument('prog1', type=str, metavar='prog-1',
                                 help='Primer programa')
        positionals.add_argument('prog2', type=str, metavar='prog-2',
                                 help='Segundo programa')

        arguments = parser.add_argument_group('Argumentos opcionales')
        arguments.add_argument("-r", "--replay", action='store_true',
                               dest='replay', help=self.HELP_REPLAY)
        arguments.add_argument("-t", "--texto", action='store_true',
                               dest='text_only', help=self.HELP_TEXT)
        arguments.add_argument("-h", "--help", action='help',
                               help=self.HELP_MESSAGE)
        
        self.options = parser.parse_args()
    
    def run(self):
        self.parse_cmdline()
        try:
            game_manager = GameManager.for_options(self.options)
            game_manager.start()
        except GameException, e:
            logging.log(logging.ERROR, str(e))
            message = 'ejército %s descalificado' % e.get_army_name()
            logging.log(logging.INFO, message)
        except Exception, e:
            logging.log(logging.ERROR, str(e))
        else:
            game_manager.end()
            
            
if __name__ == '__main__':
    Main().run()            