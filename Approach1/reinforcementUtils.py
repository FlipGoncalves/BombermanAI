from reinforcementConsts import Reinforcement

# Function to check if valid position in board
def check_if_valid_position(in_map, pos):
    return len(in_map) > pos[1] and pos[1] > 0 and len(in_map[pos[1]]) > pos[0] and pos[0] > 0

# Function to check if the position is a valid move
def check_if_valid_move(in_map, pos):
    return check_if_valid_position(in_map, pos) \
        and in_map[pos[1]][pos[0]] == Reinforcement.Step

# Function to check if the position isn't an indestructible wall
def check_if_not_indestructible_wall(in_map, pos):
    return check_if_valid_position(in_map, pos) \
        and in_map[pos[1]][pos[0]] != Reinforcement.Indestructive_Wall

# Function to check if the position isn't a destructive wall
def check_if_not_destructible_wall(in_map, pos):
    return check_if_valid_position(in_map, pos) \
        and in_map[pos[1]][pos[0]] != Reinforcement.Destructive_Wall_Exit \
        and in_map[pos[1]][pos[0]] != Reinforcement.Destructive_Wall

# Function to check if the position isn't an enemy
def check_if_not_enemy(in_map, pos):
    return check_if_valid_position(in_map, pos) \
        and in_map[pos[1]][pos[0]] != Reinforcement.Enemy_Position \
        and in_map[pos[1]][pos[0]] != Reinforcement.Enemy_Area \
        and in_map[pos[1]][pos[0]] != Reinforcement.Enemy_Bomb

# Function to check if the position isn't the player
def check_if_not_player(in_map, pos):
    return check_if_valid_position(in_map, pos) \
        and in_map[pos[1]][pos[0]] != Reinforcement.Player

# Function to check if the position isn't the player
def check_if_not_bomb(in_map, pos):
    return check_if_valid_position(in_map, pos) \
        and in_map[pos[1]][pos[0]] != Reinforcement.Bomb_Damage \
        and in_map[pos[1]][pos[0]] != Reinforcement.Bomb_Drop_Position

# Function to check if the position isn't everything
def check_if_not_everything(in_map, pos):
    return check_if_not_player(in_map, pos) \
        and check_if_not_enemy(in_map, pos) \
        and check_if_not_destructible_wall(in_map, pos) \
        and check_if_not_indestructible_wall(in_map, pos) \
        and check_if_not_bomb(in_map, pos)