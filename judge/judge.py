import logging

from collections import defaultdict
from math import sqrt

from commander import Commander
from context import GameContext
from names import NameGenerator
from soldier import Soldier
from validator import Validator


class Judge(object):
    
    def __init__(self, manager):
        programs = manager.get_programs()
        self.commanders = map(lambda program: Commander(program), programs)
        self.manager = manager
        self.context = GameContext()
        self.territory = defaultdict(list)
        self.soldiers = dict()
        self.validator = Validator(self)
        
    def get_commanders(self):
        return self.commanders
    
    def get_context(self):
        return self.context
        
    def get_soldier_by_name(self, name):
        return self.soldiers.get(name, None)
    
    def get_soldier_positions_in_range(self, soldier):
        range = soldier.get_range()
        position = soldier.get_position()
        return self.get_positions_in_range(position, range)
        
    def get_positions_in_range(self, position, s_range):
        rx, ry = s_range
        px, py = position
        n = self.context.get_territory_rows()
        m = self.context.get_territory_columns()
        return [(x,y) for x in range(max(0, px-ry), 1+min(m, px+ry))
                      for y in range(max(0, py-rx), 1+min(n, py+rx))]    
        
    def build_soldier_from(self, index, name):
        energy = self.context.get_max_energy()
        range = self.context.get_soldier_ranges()[index]
        return Soldier(name, energy, range)
        
    def build_soldiers_from(self, names):
        soldiers = list()
        for index, name in enumerate(names):
            soldier = self.build_soldier_from(index, name)
            self.soldiers[name] = soldier
            soldiers.append(soldier)
        return soldiers
        
    def update_soldiers_from(self, placed_soldiers):
        for placed_soldier in placed_soldiers:
            name = placed_soldier.get_name()
            soldier = self.get_soldier_by_name(name)
            position = placed_soldier.get_position()
            soldier.set_position(position)
            self.territory[position].append(soldier)         
        
    def place_army(self, commander, soldiers):
        message = 'Posicionando soldados de %s' % commander.get_army_name()
        logging.log(logging.INFO, message)
        commander.set_army(soldiers)
        placed_soldiers = commander.place_army_using(self.context)
        self.validate(placed_soldiers)
        self.update_soldiers_from(placed_soldiers)
        
    def place_armies(self):
        max_soldiers = self.context.get_max_soldiers()
        total_soldiers = max_soldiers * len(self.commanders)
        names = NameGenerator().generate(total_soldiers)
        for index, commander in enumerate(self.commanders):
            soldier_names = names[index*max_soldiers : 
                                  (index+1)*max_soldiers]
            soldiers = self.build_soldiers_from(soldier_names)
            self.place_army(commander, soldiers)
        
    def broadcast_enemies(self):
        for index, commander in enumerate(self.commanders):
            enemies = list(self.commanders)
            del enemies[index]
            commander.add_enemies(enemies)
        
    def run(self):
        self.place_armies()
        self.broadcast_enemies()
        self.run_game()
        
    def run_game(self):
        while self.should_run():
            self.process_current_status()
            message = 'Procesando turno %d' %\
                        self.context.get_current_turn()
            logging.log(logging.INFO, message)
            actions = self.get_all_actions()
            self.validate(actions)
            self.manager.process_actions(actions)
            self.execute_actions(actions)
        self.process_current_status()
            
    def should_run(self):
        current_turn = self.context.get_current_turn()
        max_turns = self.context.get_max_turns()
        some_army_won = self.check_if_some_army_already_won()
        return not some_army_won and current_turn < max_turns
    
    def check_if_some_army_already_won(self):
        for (index, commander) in enumerate(self.commanders):
            enemies = list(self.commanders)
            del enemies[index]
            if all(map(self.all_enemy_soldiers_are_dead, enemies)):
                return True
        return False
        
    def all_enemy_soldiers_are_dead(self, enemy):
        soldiers = enemy.get_army()
        return all([soldier.get_energy() == 0 for soldier in soldiers])
        
    def process_current_status(self):
        self.context.increment_current_turn()
        self.manager.process_soldiers(self.soldiers.values())
                                               
    def get_all_actions(self):
        actions = list()
        for commander in self.commanders:
            commander_actions = commander.make_actions_using(self.context)
            actions.extend(commander_actions)
        return actions
        
    def validate(self, objects):
        self.validator.validate(objects)
    
    def execute_actions(self, actions):
        displacements = self.get_displacements_on(actions)
        attacks = self.get_attacks_on(actions)
        self.execute_displacements(displacements)
        self.execute_attacks(attacks)
        
    def get_displacements_on(self, actions):
        return filter(lambda action: action.is_displacement(), actions)
    
    def get_attacks_on(self, actions):
        return filter(lambda action: action.is_attack(), actions)
    
    def execute_displacements(self, actions):
        for action in actions:
            soldier_name = action.get_soldier().get_name()
            soldier = self.soldiers[soldier_name]
            old_position = soldier.get_position()
            new_position = action.get_position()
            soldier.set_position(new_position)
            self.territory[old_position].remove(soldier)
            self.territory[new_position].append(soldier)
            
    def execute_attacks(self, actions):
        for action in actions:
            target = action.get_position()
            attack_range = self.context.get_attack_range()
            positions_in_range = self.get_positions_in_range(target,
                                                             attack_range)
            self.spread_damage(target, positions_in_range)

    def spread_damage(self, target, positions):
        for position in positions:
            distance = self.get_distance_between(target, position)
            soldiers = self.territory[position]
            map(lambda soldier: self.set_new_energy(distance, soldier),
                soldiers)
            
    def set_new_energy(self, distance, soldier):
        old_energy = soldier.get_energy()
        max_energy = self.context.get_max_energy()
        damage = min(old_energy, max_energy/2**distance)
        new_energy = int(old_energy - damage)
        soldier.set_energy(new_energy)
    
    def get_distance_between(self, position1, position2):
        x1, y1 = position1
        x2, y2 = position2
        return sqrt((x1-x2)**2 + (y1-y2)**2)
    
    def get_results(self):
        score = dict()
        for commander in self.commanders:
            army_name = commander.get_army_name()
            army_score = self.get_score_of(army_name)
            score[army_name] = army_score
        if not self.all_equal(score.values()):
            max_score = max(score.values())
            winner = filter(lambda (army, points): points == max_score,
                            score.items())[0][0]
            return (winner, score)
        else:
            return (None, score)
    
    def all_equal(self, values):
        return len(set(values)) == 1
    
    def get_score_of(self, army):
        points = map(lambda soldier: self.get_points_from(soldier, army),
                     self.soldiers.values())
        return sum(points)
    
    def get_points_from(self, soldier, army):
        max_energy = self.context.get_max_energy()
        points = 0
        if soldier.get_army_name() != army:
            points = max_energy - soldier.get_energy()
        return points
