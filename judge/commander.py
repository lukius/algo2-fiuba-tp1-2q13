import random

from exception import MissingFileException, ParsingException, ProgramCrash
from file import FileReader, FileWriter, FileUtils
from program import Program, ProgramArguments


class Commander(object):
    
    def __init__(self, program):
        self.program = Program(program)
        self.army = list()
        self.enemies = list()
        self.army_name = self.find_army_name()
        
    def find_army_name(self):
        try:
            name = self.do_find_army_name()
        except Exception:
            # If program fails to implement -n properly, just choose
            # a random name.
            name = 'army-%d'% random.randint(1,10000000)
        return name
        
    def do_find_army_name(self):
        arguments = ProgramArguments()
        reader = FileReader(self)
        output_filename = FileUtils.get_new_filename()
        arguments.add('-n')
        arguments.add('-o', output_filename)
        self.program.execute(arguments)
        name = reader.read_name(output_filename)
        FileUtils.remove_file(output_filename)
        return name  
        
    def get_army_name(self):
        return self.army_name
        
    def get_army(self):
        return self.army
    
    def set_army(self, soldiers):
        map(self.set_army_on_soldier, soldiers)
        self.army = soldiers
    
    def set_army_on_soldier(self, soldier):
        army_name = self.get_army_name()
        soldier.set_army_name(army_name)
    
    def add_enemies(self, enemies):
        self.enemies.extend(enemies)
        
    def read_file_or_raise(self, filename, writer, context):
        reader = FileReader(context)
        try:
            data = reader.read(filename)
        except IOError:
            raise MissingFileException(self.army_name, self.program,
                                       writer.get_filename())
        except ParsingException, e:
            e.set_army_name(self.army_name)
            raise e
        else:
            writer.remove_file()
        return data
        
    def execute_program_using(self, context, enemies=None):
        arguments = ProgramArguments()
        writer = FileWriter(context)
        output_filename = FileUtils.get_new_filename()
        writer.write(self.army, enemies)
        arguments.add('-i', writer.get_filename())
        arguments.add('-o', output_filename)
        self.execute_program_with(arguments)
        data = self.read_file_or_raise(output_filename, writer, context)
        FileUtils.remove_file(output_filename)
        return data
    
    def execute_program_with(self, arguments):
        try:
            self.program.execute(arguments)
        except ProgramCrash, e:
            e.set_army_name(self.army_name)
            raise e
        
    def place_army_using(self, context):
        soldiers = self.execute_program_using(context)
        map(self.set_army_on_soldier, soldiers)
        return soldiers
    
    def make_actions_using(self, context):
        actions = self.execute_program_using(context, self.enemies)
        map(lambda action: self.set_army_on_soldier(action.get_soldier()),
            actions)
        return actions
        
    def __hash__(self):
        return hash(self.get_army_name())
    
    def __eq__(self, commander):
        return self.get_army_name() == commander.get_army_name()
