import os
import re
import random
import shutil

from soldier import Soldier
from action import Action
from exception import ParsingException


class FileUtils(object):
    
    @classmethod
    def get_new_filename(cls):
        return 'file_%d' % int(random.randint(1,1000000))
    
    @classmethod
    def copy_file(cls, source, destination):
        shutil.copy(source, destination)
        
    @classmethod
    def path_exists(cls, path):
        return os.path.exists(path)
    
    @classmethod
    def remove_file(cls, filename):
        try:
            os.remove(filename)
        except:
            pass


class FileReader(object):

    def __init__(self, context=None):
        self.context = context
        self.placement_re = re.compile('(.*)' + '\s+(\d+)'*5)
        self.action_re = re.compile('(.*)' + '\s+(\d+)'*5 + '\s+([AD])' +\
                                    '\s+(\d+)'*2)
    
    def match_regexp(self, regexp, text):
        match = regexp.match(text)
        if match is None:
            raise ParsingException(text)
        return match.groups()
    
    def read_soldier(self, line):
        groups = self.match_regexp(self.placement_re, line)
        name = groups[0]
        energy = int(groups[1])
        range = (int(groups[2]), int(groups[3]))
        position = (int(groups[4]), int(groups[5]))
        return Soldier(name, energy, range, position)
    
    def read_action(self, line):
        groups = self.match_regexp(self.action_re, line)
        name = groups[0]
        energy = int(groups[1])
        range = (int(groups[2]), int(groups[3]))        
        position = (int(groups[4]), int(groups[5]))
        action = groups[6]
        target = (int(groups[7]), int(groups[8]))        
        soldier = Soldier(name, energy, range, position)
        return Action.from_string(action).for_soldier(soldier).on(target)
    
    def read_army_placement(self, lines):
        return map(self.read_soldier, lines)
    
    def read_army_actions(self, lines):
        return map(self.read_action, lines)
    
    def read_name(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
            name = lines[0].strip()
        return name
    
    def read(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
            if self.context.get_current_turn() == 0:
                data = self.read_army_placement(lines)
            else:
                data = self.read_army_actions(lines)
        return data


class FileWriter(object):
    
    def __init__(self, context):
        self.context = context
        self.filename = FileUtils.get_new_filename()

    def remove_file(self):
        FileUtils.remove_file(self.filename)
        
    def get_filename(self):
        return self.filename
        
    def write_context(self, file):
        current_turn = self.context.get_current_turn()
        max_turns = self.context.get_max_turns()
        n = self.context.get_territory_rows()
        m = self.context.get_territory_columns()
        attack_range = self.context.get_attack_range()
        file.write('%d\n' % current_turn)
        file.write('%d\n' % max_turns)
        file.write('%d %d\n' % (n, m))
        file.write('%d %d\n' % (attack_range[0], attack_range[1]))
        file.write('\n')
        
    def write_soldiers(self, file, soldiers):
        for soldier in soldiers:
            name = soldier.get_name()
            energy = soldier.get_energy()
            if energy == 0:
                continue
            range = soldier.get_range()
            if self.context.get_current_turn() == 0:
                soldier_line = '%s %d %d %d\n' % (name, energy,
                                                  range[0], range[1])
            else:
                position = soldier.get_position()
                soldier_line = '%s %d %d %d %d %d\n' % (name, energy,
                                                        range[0], range[1],
                                                        position[0],
                                                        position[1])
            file.write(soldier_line)
        
    def write_enemies(self, file, enemies):
        if enemies is not None:
            for enemy in enemies:
                file.write('\n')
                self.write_soldiers(file, enemy.get_army())
        
    def write(self, soldiers, enemies=None):
        with open(self.filename, 'w') as file:
            self.write_context(file)
            self.write_soldiers(file, soldiers)
            self.write_enemies(file, enemies)
            

class JSONWriter(object):
    
    SOLDIERS_FILENAME = 'iteration'
    ACTIONS_FILENAME = 'action'
    CONFIG_FILENAME = 'config'
    
    def __init__(self, base_directory, relative_directory, army_names):
        self.base_directory = base_directory
        self.relative_directory = relative_directory
        self.army_names = army_names
        self.output_directory = '%s/%s' % (base_directory, relative_directory)
        self.make_directory(self.output_directory)
        self.army_ids = {name:(index+1)
                         for (index,name) in enumerate(army_names)}
        
    def get_output_directory(self):
        return self.output_directory
    
    def make_directory(self, directory):
        try:
            os.mkdir(directory)
        except:
            pass
    
    def serialize_soldier(self, soldier):
        template = '{"name":"%s","row":%d,"col":%d,' +\
                    '"e":%d,"rx":%d,"ry":%d,"army":%d}'
        name = soldier.get_name()
        energy = soldier.get_energy()
        row, col = soldier.get_position()
        rx, ry = soldier.get_range()
        army_id = self.army_ids[soldier.get_army_name()]
        return template % (name, row, col, energy, rx, ry, army_id)
        
    def serialize_action(self, action):
        template = '{"name":"%s","action":"%s","x":%d,"y":%d}'
        name = action.get_soldier().get_name()
        action_type = action.get_type()
        x, y = action.get_position()
        return template % (name, action_type, x, y)
        
    def write_soldiers(self, soldiers, context):
        self.write_using(soldiers, self.serialize_soldier,
                         self.SOLDIERS_FILENAME, context)
    
    def write_actions(self, actions, context):
        self.write_using(actions, self.serialize_action, self.ACTIONS_FILENAME,
                         context)
            
    def write_using(self, objects, serialization_method, filename, context):
        path = '%s/%s%d' % (self.output_directory, filename,
                            context.get_current_turn())
        with open(path, 'w') as file:
            file.write('[')
            serialized_objects = ','.join(map(serialization_method, objects))
            file.write(serialized_objects)
            file.write(']')
            
    def write_config_file(self, context):
        # Save config file to battle output directory so we can replay this
        # battle later.
        path = '%s/%s' % (self.output_directory, self.CONFIG_FILENAME)
        with open(path, 'w') as file:
            self.write_config_values(file, context)
        # Copy config file to base UI directory in order to run visualization.
        FileUtils.copy_file(path, self.base_directory)
        
    def write_config_values(self, file, context):
        gx, gy = context.get_attack_range()
        army1_name = self.army_names[0]
        army2_name = self.army_names[1]        
        file.write('{')
        file.write('"n":%d,' % context.get_territory_rows())
        file.write('"m":%d,' % context.get_territory_columns())
        file.write('"e":%d,' % context.get_max_energy())
        file.write('"t":%d,' % context.get_current_turn())
        file.write('"gx":%d,' % gx)
        file.write('"gy":%d,' % gy)
        file.write('"iteration_filename":"%s/%s",' %
                   (self.relative_directory, self.SOLDIERS_FILENAME))
        file.write('"action_filename":"%s/%s",' %
                   (self.relative_directory, self.ACTIONS_FILENAME))
        file.write('"army1_name":"%s",' % army1_name)
        file.write('"army2_name":"%s"' % army2_name)            
        file.write('}')