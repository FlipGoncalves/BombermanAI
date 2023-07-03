from enum import Enum, IntEnum


class Area(Enum):
    Range_One = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    Range_Two = [(1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)]

    Enemy_Bomb_Position = [(2, 0), (-2, 0), (0, 2), (0, -2)]
    Enemy_Area_Position = [(1, 0), (-1, 0), (0, 1), (0, -1)]


class Reinforcement(float, Enum):
    # Valid Move
    Valid_Move = -0.01,

    # Invalid Move
    Indestructible_Wall = -100,

    # Damage
    Damage = -55,

    # Reward
    Reward = 30,

    # Powerups
    Powerup = 20

    # Exit
    Exit = 50

    # Player
    Player = -10


class Powerups(IntEnum):
    Bombs = 1,
    Flames = 2,
    Speed = 3,
    Wallpass = 4,
    Detonator = 5,
    Bombpass = 6,
    Flamepass = 7,
    Mystery = 8


class Speed(IntEnum):
    SLOWEST = 1,
    SLOW = 2,
    NORMAL = 3,
    FAST = 4


class Smart(IntEnum):
    LOW = 1,
    NORMAL = 2,
    HIGH = 3
