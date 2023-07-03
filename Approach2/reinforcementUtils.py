from reinforcementConsts import Reinforcement


# Function to check if the position is within the map
def check_in_map(in_map, pos):
    return (pos[0] > 0 and pos[1] > 0) and len(in_map) > pos[1] and len(in_map[pos[1]]) > pos[0]


# Function to check if the position is a valid move (and if it's within the map)
def check_if_valid_move(in_map, pos):
    return check_in_map(in_map, pos) and in_map[pos[1]][pos[0]] == Reinforcement.Valid_Move


# Function to check if the position is an indestructible wall (and if it's within the map)
def check_if_indestructible_wall(in_map, pos):
    return check_in_map(in_map, pos) and in_map[pos[1]][pos[0]] == Reinforcement.Indestructible_Wall


# Function to check if the position isn't an indestructible wall (and if it's within the map)
def check_if_not_indestructible_wall(in_map, pos):
    return check_in_map(in_map, pos) and in_map[pos[1]][pos[0]] != Reinforcement.Indestructible_Wall


def check_if_bomb_target(in_map, wall, bombs):

    # All possible relative positions
    area = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for bomb in bombs:

        # Obtain bomb position
        bomb_position = bomb[0]

        # Obtain bomb radius
        bomb_radius = bomb[2]

        # If the wall is within the bomb radius
        for positions in area:

            for current_range in range(1, bomb_radius + 1):

                # Obtain the position
                position = (bomb_position[0] + positions[0] * current_range,
                            bomb_position[1] + positions[1] * current_range)

                # If the wall is within the bomb radius
                if position == wall:
                    return True

                # If the position is another wall
                if check_if_indestructible_wall(in_map, position):
                    break

        return False
