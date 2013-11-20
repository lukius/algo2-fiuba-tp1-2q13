import logging
import os
import SimpleHTTPServer
import SocketServer
import subprocess
import threading

from exception import GameException, WebBrowsersMissingException
from file import JSONWriter, FileUtils
from judge import Judge


class LeafSubclassRetriever(object):
    
    def __init__(self, base_class):
        self.base_class = base_class
          
    def value(self):
        direct_subclasses = self.base_class.__subclasses__()
        leaf_subclasses = list()
        for cls in direct_subclasses:
            if( len(cls.__subclasses__()) > 0 ):
                leaf_subclasses += LeafSubclassRetriever(cls).value()
            else:
                leaf_subclasses.append(cls)
        return leaf_subclasses
    

class GameManager(object):
    
    @classmethod
    def for_options(cls, options):
        subclasses = LeafSubclassRetriever(cls).value()
        manager_class = filter(lambda subclass: subclass.handles(options),
                               subclasses)[0]
        return manager_class(options)
    
    @classmethod
    def handles(cls, options):
        raise NotImplementedError('Subclass responsibility')    
    
    def __init__(self, options):
        self.options = options
        self.judge = Judge(self)
        
    def get_programs(self):
        return [self.options.prog1, self.options.prog2]      
        
    def start(self):
        self.judge.run()
        
    def end(self):
        logging.log(logging.INFO,
                    'Batalla finalizada! Mostrando resultados...')        
        self.display_results()        
    
    def process_actions(self, actions):
        raise NotImplementedError('Subclass responsibility')
    
    def process_soldiers(self, soldiers):
        raise NotImplementedError('Subclass responsibility')
    
    def display_results(self):
        raise NotImplementedError('Subclass responsibility')

        
class TextBasedGameManager(GameManager):
    
    @classmethod
    def handles(cls, options):
        return options.text_only
    
    def process_actions(self, actions):
        pass
    
    def process_soldiers(self, soldiers):
        pass
        
    def display_results(self):
        winner, score = self.judge.get_results()
        message = ' -- '.join(['%s: %d puntos' % (army, points)
                               for (army, points) in score.items()])
        logging.log(logging.INFO, message)
        if winner is not None:
            logging.log(logging.INFO, 'Ganador: %s' % winner)        


class GraphicsBasedGameManager(GameManager):
    
    ADDRESS = '127.0.0.1'
    PORT = 8080
    BROWSERS = ['google-chrome', 'chromium-browser']
    OUTPUT_DIRECTORY = 'judge/ui'
    
    def __init__(self, options):
        GameManager.__init__(self, options)
        self.browser = self.find_browser()
        self.server_initialized_event = threading.Event()
        
    def process_actions(self, actions):
        raise NotImplementedError('Subclass responsibility')
    
    def process_soldiers(self, soldiers):
        raise NotImplementedError('Subclass responsibility')
    
    def display_results(self):
        raise NotImplementedError('Subclass responsibility')
    
    def browser_is_available(self, browser):
        with open(os.devnull, 'w') as devnull:
            return_code = subprocess.call(['which', browser], stdout=devnull,
                                          stderr=subprocess.STDOUT)
            return return_code == 0
        
    def find_browser(self):
        selected_browser = None
        for browser in self.BROWSERS:
            if self.browser_is_available(browser):
                selected_browser = browser
                break
        return selected_browser
    
    def start(self):
        if self.browser is None:
            raise WebBrowsersMissingException(self.BROWSERS)
        GameManager.start(self)
    
    def get_army_names(self):
        commanders = self.judge.get_commanders()
        return map(lambda commander: commander.get_army_name(), commanders)
    
    def get_relative_directory(self):
        army_names = self.get_army_names()
        return '-'.join(army_names)    
        
    def show_battle(self):
        self.start_web_server_on(self.OUTPUT_DIRECTORY)
        self.launch_web_browser()        
    
    def start_web_server_on(self, directory):
        thread = threading.Thread(target=self.do_start_web_server_on,
                                  args=(directory,))
        thread.setDaemon(True)
        thread.start()
        self.server_initialized_event.wait()
        
    def do_start_web_server_on(self, directory):
        class CustomTCPServer(SocketServer.TCPServer):
            allow_reuse_address = True
            
        os.chdir(directory)
        handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        server = CustomTCPServer((self.ADDRESS, self.PORT), handler)
        self.server_initialized_event.set()
        server.serve_forever()
    
    def launch_web_browser(self):
        url = 'http://%s:%d/war.html' % (self.ADDRESS, self.PORT)
        subprocess.call([self.browser, '--app=%s' % url, '--window-size=1270,1000',
                         '--user-data-dir=temp'])
        

class GraphicableGameManager(GraphicsBasedGameManager):
    
    @classmethod
    def handles(cls, options):
        return not options.text_only and not options.replay
    
    def __init__(self, options):
        GraphicsBasedGameManager.__init__(self, options)
        army_names = self.get_army_names()
        relative_directory = self.get_relative_directory()
        self.writer = JSONWriter(self.OUTPUT_DIRECTORY, relative_directory,
                                 army_names)
        
    def process_actions(self, actions):
        context = self.judge.get_context()
        self.writer.write_actions(actions, context)
    
    def process_soldiers(self, soldiers):
        context = self.judge.get_context()
        self.writer.write_soldiers(soldiers, context)
        
    def write_config_file(self):
        context = self.judge.get_context()
        self.writer.write_config_file(context)

    def display_results(self):
        self.write_config_file()
        self.show_battle()
        
        
class ReplayableGameManager(GraphicsBasedGameManager):
    
    @classmethod
    def handles(cls, options):
        return not options.text_only and options.replay
    
    def process_actions(self, actions):
        pass
    
    def process_soldiers(self, soldiers):
        pass
    
    def display_results(self):
        pass
    
    def end(self):
        pass
    
    def start(self):
        relative_directory = self.get_relative_directory()
        battle_directory = '%s/%s' % (self.OUTPUT_DIRECTORY,
                                      relative_directory)
        if FileUtils.path_exists(battle_directory):
            logging.log(logging.INFO, 'Repitiendo batalla...')
            self.copy_config_file_from(battle_directory)
            self.show_battle()
        else:
            message = 'Los archivos de la batalla no se encontraron'
            logging.log(logging.INFO, message)
            
    def copy_config_file_from(self, directory):
        config_file = '%s/%s' % (directory, JSONWriter.CONFIG_FILENAME)
        FileUtils.copy_file(config_file, self.OUTPUT_DIRECTORY)