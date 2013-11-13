class Soldier(object):
    
    def __init__(self, name, energy, range, position=None):
        self.name = name
        self.energy = energy
        self.range = range
        if position is not None:
            self.position = position
        
    def get_name(self):
        return self.name
    
    def get_energy(self):
        return self.energy
    
    def get_range(self):
        return self.range
    
    def get_position(self):
        return self.position
        
    def get_army_name(self):
        return self.army_name
        
    def set_position(self, position):
        self.position = position
    
    def set_army_name(self, name):
        self.army_name = name
        
    def set_energy(self, energy):
        self.energy = energy
        
    def __eq__(self, soldier):
        return self.name == soldier.get_name()
        
    def __str__(self):
        return '<%s : e=%d, r=%s, p=%s>' % (self.name, self.energy,
                                            str(self.range),
                                            str(self.position))