

class Action(object):
    
    @classmethod
    def from_string(cls, string):
        subclasses = cls.__subclasses__()
        return filter(lambda subclass: subclass.handles(string), subclasses)[0]
    
    @classmethod
    def handles(cls, string):
        raise NotImplementedError
    
    @classmethod
    def for_soldier(cls, soldier):
        action = cls(soldier)
        return action
    
    def __init__(self, soldier):
        self.soldier = soldier
    
    def on(self, position):
        self.position = position
        return self
    
    def get_position(self):
        return self.position
    
    def get_soldier(self):
        return self.soldier
    
    def get_army_name(self):
        return self.soldier.get_army_name()
    
    def is_attack(self):
        return False
    
    def is_displacement(self):
        return False
    
    def __str__(self):
        soldier = str(self.soldier)
        action = self.get_type()
        position = str(self.get_position())
        return '%s %s -> %s' % (soldier, action, position)
    
    
class AttackAction(Action):
    
    @classmethod
    def handles(cls, string):
        return string == 'A'
    
    def get_type(self):
        return 'A'
    
    def is_attack(self):
        return True
    
    
class DisplacementAction(Action):
    
    @classmethod
    def handles(cls, string):
        return string == 'D'
    
    def get_type(self):
        return 'D'
    
    def is_displacement(self):
        return True    