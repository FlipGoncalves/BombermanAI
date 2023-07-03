from enum import Enum

class Area(Enum):
    Range_One = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    Range_Two = [(1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)]

    Enemy_Bomb_Position = [(2,0),(-2,0),(0,2),(0,-2)]
    Enemy_Area_Position = [(1,0),(-1,0),(0,1),(0,-1)]

class Reinforcement(float, Enum):
    # wall we cant break
    Indestructive_Wall = -100,
    # wall we can break
    Destructive_Wall = 6,
    Destructive_Wall_Exit = 4.5,
    # enemy
    Enemy_Area = -8,
    Enemy_Position = -20,
    Enemy_Bomb = 20,
    # damage given by the bomb when it explodes
    Bomb_Drop_Position = -10,
    Bomb_Damage = -10,
    # miscellanious
    Step = -0.01,
    Player = -0.02,
    Powerup = 10,
    Exit = 50,

    def __str__(self) -> str:
        return str(self.value)