class GameContext(object):

    MAX_TURNS = 20
    MAX_ENERGY = 100
    SOLDIERS = 15
    TERRITORY_ROWS = 25
    TERRITORY_COLUMNS = 25
    ATTACK_RANGE = (2,2)
    SOLDIER_RANGES = [(5,5),(4,4),(4,4),(3,3),(3,3),
                      (3,3),(3,3),(3,2),(3,2),(2,3),
                      (2,3),(1,6),(6,1),(1,4),(4,1)]
    CURRENT_TURN = 0
    
    def get_max_turns(self):
        return self.MAX_TURNS
    
    def get_max_energy(self):
        return self.MAX_ENERGY
    
    def get_territory_rows(self):
        return self.TERRITORY_ROWS
    
    def get_territory_columns(self):
        return self.TERRITORY_COLUMNS
    
    def get_attack_range(self):
        return self.ATTACK_RANGE
    
    def get_soldier_ranges(self):
        return self.SOLDIER_RANGES
    
    def get_max_soldiers(self):
        return self.SOLDIERS
    
    def get_current_turn(self):
        return self.CURRENT_TURN
    
    def increment_current_turn(self):
        self.CURRENT_TURN += 1