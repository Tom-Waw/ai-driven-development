"""This module contains the classes for the game characters."""

class Character:
    def __init__(self, name, character_type, appearance):
        self.name = name
        self.character_type = character_type
        self.appearance = appearance
        self.stats = {}
        self.weapon = None
        """Set the statistics for the character."""

        self.armor = None
        """Choose a weapon for the character."""


        """Choose armor for the character."""

    def set_stats(self, stats):
        self.stats = stats
"""Class representing a Warrior character."""


    def choose_weapon(self, weapon):
        self.weapon = weapon
"""Class representing a Mage character."""


    def choose_armor(self, armor):
        self.armor = armor
"""Class representing a Rogue character."""



class Warrior(Character):
    def __init__(self, name, appearance):
        super().__init__(name, 'Warrior', appearance)


class Mage(Character):
    def __init__(self, name, appearance):
        super().__init__(name, 'Mage', appearance)


class Rogue(Character):
    def __init__(self, name, appearance):
        super().__init__(name, 'Rogue', appearance)
