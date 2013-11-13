import random
import string


vowels = 'aeiou'
consonants = filter(lambda char: char not in vowels + 'yq', string.lowercase)


class NameGenerator(object):

    def consonant(self):
        global consonants
        return random.choice(consonants)
        
    def vowel(self):
        global vowels
        return random.choice(vowels)
        
    def randname1(self, size):
        return ''.join([self.vowel() if i%3 else self.consonant()
                        for i in range(size)])
                        
    def randname2(self, size):
        return ''.join([self.vowel() if i%3 == 1 else self.consonant()
                        for i in range(size)])
                        
    def randname3(self, size):
        return ''.join([self.consonant(), self.vowel(), self.vowel(),
                        self.consonant(), self.consonant(), self.vowel()])
        
    def get_name(self):
        size = random.randint(3, 7)
        method_index = random.randint(1, 3)
        method = getattr(self, 'randname%d' % method_index)
        return method(size)
    
    def generate(self, amount):
        names = set()
        while len(names) < amount:
            names.add(self.get_name())
        return list(names)