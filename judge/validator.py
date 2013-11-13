# -*- coding: utf-8 -*- 

from action import Action
from exception import ValidationException
from soldier import Soldier


class Validator(object):
    
    def __init__(self, judge):
        self.judge = judge
        
    def validate_object(self, obj):
        rules = ValidationRule.choose_for(obj)
        for rule_class in rules:
            rule = rule_class(self.judge, obj)
            if not rule.check():
                raise ValidationException(rule)
        
    def validate(self, objects):
        map(self.validate_object, objects)


class ValidationObject(object):
    
    @classmethod
    def build_from(cls, obj):
        subclasses = cls.__subclasses__()
        adapter = filter(lambda subclass: subclass.handles(obj), subclasses)[0]
        return adapter(obj)
    
    @classmethod
    def handles(cls, obj):
        raise NotImplementedError('Subclass responsibility')
    
    def __init__(self, obj):
        self.object = obj


class SoldierValidationWrapper(ValidationObject):
    
    @classmethod
    def handles(cls, obj):
        return isinstance(obj, Soldier)
    
    def get_soldier(self):
        return self.object
    
    
class ActionValidationWrapper(ValidationObject):
    
    @classmethod
    def handles(cls, obj):
        return isinstance(obj, Action)
    
    def get_soldier(self):
        return self.object.get_soldier()
    
    def get_position(self):
        return self.object.get_position()    


class ValidationRule(object):
    
    @classmethod
    def choose_for(cls, obj):
        subclasses = cls.__subclasses__()
        return filter(lambda subclass: subclass.handles(obj), subclasses)
    
    @classmethod
    def handles(cls, obj):
        raise NotImplementedError('Subclass responsibility') 
    
    @classmethod
    def name(cls):
        raise NotImplementedError('Subclass responsibility') 
    
    def __init__(self, judge, obj):
        self.judge = judge
        self.obj = ValidationObject.build_from(obj)
        
    def get_object(self):
        return self.obj
    
    def check(self):
        raise NotImplementedError('Subclass responsibility')
    
    def get_string(self):
        raise NotImplementedError('Subclass responsibility')        
    
    def __str__(self):
        return '%s: %s' % (self.name(), self.get_string())


class ActionOnKnownSoldierRule(ValidationRule):
    
    @classmethod
    def handles(cls, obj):
        return isinstance(obj, Action) or isinstance(obj, Soldier)
    
    @classmethod
    def name(cls):
        return 'soldado desconocido'    
    
    def check(self):
        soldier_name = self.obj.get_soldier().get_name()
        return self.judge.get_soldier_by_name(soldier_name) is not None
    
    def get_string(self):
        return str(self.obj.get_soldier())


class SoldierNotDeadRule(ValidationRule):
    
    @classmethod
    def handles(cls, obj):
        return isinstance(obj, Action)
    
    @classmethod
    def name(cls):
        return 'soldado muerto'    
    
    def check(self):
        soldier_name = self.obj.get_soldier().get_name()
        soldier_energy = self.obj.get_soldier().get_energy()
        return soldier_energy > 0
    
    def get_string(self):
        return str(self.obj.get_soldier())   
    
    
class EnergyNotChangedRule(ValidationRule):
    
    @classmethod
    def handles(cls, obj):
        return isinstance(obj, Action) or isinstance(obj, Soldier)
    
    @classmethod
    def name(cls):
        return 'energía modificada'
    
    def get_energies(self):
        soldier_name = self.obj.get_soldier().get_name()
        soldier_energy = self.obj.get_soldier().get_energy()
        soldier = self.judge.get_soldier_by_name(soldier_name)
        current_energy = soldier.get_energy()    
        return current_energy, soldier_energy 
    
    def check(self):
        old_energy, new_energy = self.get_energies()
        return old_energy == new_energy
    
    def get_string(self):
        name = self.obj.get_soldier().get_name()
        old_energy, new_energy = self.get_energies()
        return '%s antes tenía %d y ahora %d' % (name, old_energy, new_energy)
    
    
class RangeNotChangedRule(ValidationRule):
    
    @classmethod
    def handles(cls, obj):
        return isinstance(obj, Action) or isinstance(obj, Soldier)
    
    @classmethod
    def name(cls):
        return 'rango modificado'
    
    def get_ranges(self):
        soldier_name = self.obj.get_soldier().get_name()
        soldier_range = self.obj.get_soldier().get_range()
        soldier = self.judge.get_soldier_by_name(soldier_name)
        current_range = soldier.get_range()  
        return current_range, soldier_range
    
    def check(self):
        old_range, new_range = self.get_ranges()
        return old_range == new_range
    
    def get_string(self):
        name = self.obj.get_soldier().get_name()
        old_range, new_range = self.get_ranges()
        return '%s antes tenía %s y ahora %s' % (name, str(old_range),
                                                 str(new_range))
    
    
class PositionNotChangedRule(ValidationRule):
    
    @classmethod
    def handles(cls, obj):
        return isinstance(obj, Action)
    
    @classmethod
    def name(cls):
        return 'posición modificada'
    
    def get_positions(self):
        soldier_name = self.obj.get_soldier().get_name()
        soldier_position = self.obj.get_soldier().get_position()
        soldier = self.judge.get_soldier_by_name(soldier_name)
        current_position = soldier.get_position() 
        return current_position, soldier_position
    
    def check(self):
        old_position, new_position = self.get_positions()
        return old_position == new_position
    
    def get_string(self):
        name = self.obj.get_soldier().get_name()
        old_position, new_position = self.get_positions()
        return '%s antes estaba en %s y ahora en %s' % (name,
                                                        str(old_position),
                                                        str(new_position))
        
class ValidInitialPositionRule(ValidationRule):
    
    @classmethod
    def handles(cls, obj):
        return isinstance(obj, Soldier)
    
    @classmethod
    def name(cls):
        return 'posición inicial inválida'
    
    def get_positions(self):
        soldier_name = self.obj.get_soldier().get_name()
        soldier_position = self.obj.get_soldier().get_position()
        soldier = self.judge.get_soldier_by_name(soldier_name)
        current_position = soldier.get_position() 
        return current_position, soldier_position
    
    def check(self):
        x, y = self.obj.get_soldier().get_position()
        context = self.judge.get_context()
        n = context.get_territory_rows()
        m = context.get_territory_columns()
        return 0 <= x < n and 0 <= y < m 
    
    def get_string(self):
        name = self.obj.get_soldier().get_name()
        position = self.obj.get_soldier().get_position()
        return '%s está en %s' % (name, str(position))
    
    
class ValidActionTargetRule(ValidationRule):
    
    @classmethod
    def handles(cls, obj):
        return isinstance(obj, Action)
    
    @classmethod
    def name(cls):
        return 'acción fuera de rango'
    
    def check(self):
        soldier_name = self.obj.get_soldier().get_name()
        action_target = self.obj.get_position()
        soldier = self.judge.get_soldier_by_name(soldier_name)
        positions_in_range = self.judge.get_soldier_positions_in_range(soldier)
        return action_target in positions_in_range
    
    def get_string(self):
        name = self.obj.get_soldier().get_name()
        soldier = self.judge.get_soldier_by_name(name)
        range = soldier.get_range()
        position = soldier.get_position()
        action_target = self.obj.get_position()
        return '%s está en %s, tiene rango %s y su acción es sobre %s' %\
                (name, str(position), str(range), str(action_target))