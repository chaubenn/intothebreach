# DO NOT modify or add any import statements
import tkinter as tk
from typing import Union

# Model Constants
TANK_RANGE = 5
SCORPION_RANGE = 2
FIREFLY_RANGE = 5

MAX_BUILDING_HEALTH = 9

TILE_NAME = "Tile"
TILE_SYMBOL = "T"
GROUND_NAME = "Ground"
GROUND_SYMBOL = " "
MOUNTAIN_NAME = "Mountain"
MOUNTAIN_SYMBOL = "M"
BUILDING_NAME = "Building"

ENTITY_NAME = "Entity"
ENTITY_SYMBOL = "E"
MECH_NAME = "Mech"
MECH_SYMBOL = "M"
ENEMY_NAME = "Enemy"
ENEMY_SYMBOL = "N"
TANK_NAME = "TankMech"
TANK_SYMBOL = "T"
HEAL_NAME = "HealMech"
HEAL_SYMBOL = "H"
SCORPION_NAME = "Scorpion"
SCORPION_SYMBOL = "S"
FIREFLY_NAME = "Firefly"
FIREFLY_SYMBOL = "F"

TANK_DISPLAY = "\U000023F8"
HEAL_DISPLAY = "\U0001F6E1"
SCORPION_DISPLAY = "\U00010426"
FIREFLY_DISPLAY = "\U00000D9E"

# Used to get attack tiles for various entities
PLUS_OFFSETS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

# GUI Constants
GRID_SIZE = 450
SIDEBAR_WIDTH = 300
BANNER_HEIGHT = 75
CONTROL_BAR_HEIGHT = 100

BANNER_TEXT = "Into The Breach"
SIDEBAR_HEADINGS = ("Unit", "Coord", "Hp", "Dmg")

SAVE_TEXT = "Save Game"
LOAD_TEXT = "Load Game"
UNDO_TEXT = "Undo Move"
TURN_TEXT = "End Turn"

INVALID_SAVE_TITLE = "Cannot Save!"
INVALID_SAVE_MESSAGE = "You can only save at the beginning of your turn!"
IO_ERROR_TITLE = "File Error"
IO_ERROR_MESSAGE = "Cannot open specified file: "
PLAY_AGAIN_TEXT = "Would you like to play again?"

BANNER_FONT = ("Arial", 22, "bold")
ENTITY_FONT = ("Arial", 20, "bold")
SIDEBAR_FONT = ("Arial", 14, "bold")

ATTACK_COLOR = "Red"
MOVE_COLOR = "Lime"
GROUND_COLOR = "SandyBrown"
BUILDING_COLOR = "Turquoise"
DESTROYED_COLOR = "Teal"
MOUNTAIN_COLOR = "Olive"


class AbstractGrid(tk.Canvas):
    
    def __init__(
        self,
        master: Union[tk.Tk, tk.Widget],
        dimensions: tuple[int, int],
        size: tuple[int, int],
        **kwargs
    ) -> None:
        """Constructor for AbstractGrid.

        Parameters:
            master: The master frame for this Canvas.
            dimensions: (#rows, #columns)
            size: (width in pixels, height in pixels)
        """
        super().__init__(
            master,
            width=size[0] + 1,
            height=size[1] + 1,
            highlightthickness=0,
            **kwargs
        )
        self._size = size
        self.set_dimensions(dimensions)

    def set_dimensions(self, dimensions: tuple[int, int]) -> None:
        """Sets the dimensions of the grid.

        Parameters:
            dimensions: Dimensions of this grid as (#rows, #columns)
        """
        self._dimensions = dimensions

    def _get_cell_size(self) -> tuple[int, int]:
        """Returns the size of the cells (width, height) in pixels."""
        rows, cols = self._dimensions
        width, height = self._size
        return width // cols, height // rows

    def pixel_to_cell(self, x: int, y: int) -> tuple[int, int]:
        """Converts a pixel position to a cell position.

        Parameters:
            x: The x pixel position.
            y: The y pixel position.

        Returns:
            The (row, col) cell position.
        """
        cell_width, cell_height = self._get_cell_size()
        return y // cell_height, x // cell_width

    def _get_bbox(self, position: tuple[int, int]) -> tuple[int, int, int, int]:
        """Returns the bounding box of the given (row, col) position.

        Parameters:
            position: The (row, col) cell position.

        Returns:
            Bounding box for this position as (x_min, y_min, x_max, y_max).
        """
        row, col = position
        cell_width, cell_height = self._get_cell_size()
        x_min, y_min = col * cell_width, row * cell_height
        x_max, y_max = x_min + cell_width, y_min + cell_height
        return x_min, y_min, x_max, y_max

    def _get_midpoint(self, position: tuple[int, int]) -> tuple[int, int]:
        """Gets the graphics coordinates for the center of the cell at the
            given (row, col) position.

        Parameters:
            position: The (row, col) cell position.

        Returns:
            The x, y pixel position of the center of the cell.
        """
        row, col = position
        cell_width, cell_height = self._get_cell_size()
        x_pos = col * cell_width + cell_width // 2
        y_pos = row * cell_height + cell_height // 2
        return x_pos, y_pos

    def annotate_position(
        self, position: tuple[int, int], text: str, font=None
    ) -> None:
        """Annotates the cell at the given (row, col) position with the
            provided text.

        Parameters:
            position: The (row, col) cell position.
            text: The text to draw.
        """
        self.create_text(self._get_midpoint(position), text=text, font=font)

    def color_cell(self, position: tuple[int, int], color: str) -> None:
        """
        Colors the cell at the given (row, col) position with the specified
        color

        Parameters:
            position: The (row, col) cell position.
            color: The tkInter string corresponding to the desired color
        """
        self.create_rectangle(*self._get_bbox(position), fill=color)

    def clear(self):
        """Clears all child widgets off the canvas."""
        self.delete("all")


# Note: "" just allows type hint despite BreachModel not being defined in file.
def get_distance(
    game_state: "BreachModel", origin: tuple[int, int], destination: tuple[int, int]
) -> int:

    entity_tiles = set(game_state.entity_positions().keys())
    # Initialise
    searched = set()
    frontier = {origin: 0}

    while len(frontier) > 0:
        # get minimum frontier node
        min = float("inf")
        node = None
        for key, val in frontier.items():
            if val < min:
                node = key
                min = val
        # Move node to searched pile
        value = frontier.pop(node)
        searched.add(node)

        if node == destination:
            return value
        else:
            # Add children to frontier
            new_val = value + 1
            for delta in PLUS_OFFSETS:
                new_node = (node[0] + delta[0], node[1] + delta[1])
                if (
                    (new_node not in searched)
                    and (new_node not in entity_tiles)
                    and not (game_state.get_board().get_tile(new_node).is_blocking())
                    and not (frontier.get(new_node, float("inf")) <= new_val)
                ):
                    frontier[new_node] = new_val

    # We have run out of paths
    return -1

from tkinter import messagebox, filedialog
from typing import Optional, Callable


SYMBOLS = {
    TILE_NAME: TILE_SYMBOL,
    GROUND_NAME: GROUND_SYMBOL,
    MOUNTAIN_NAME: MOUNTAIN_SYMBOL,
    ENTITY_NAME: ENTITY_SYMBOL,
    MECH_NAME: MECH_SYMBOL,
    ENEMY_NAME: ENEMY_SYMBOL,
    TANK_NAME: TANK_SYMBOL,
    HEAL_NAME: HEAL_SYMBOL,
    SCORPION_NAME: SCORPION_SYMBOL,
    FIREFLY_NAME: FIREFLY_SYMBOL
}

'''Reduces code duplication of subclasses accessing symbols'''



class Tile:
    '''
    Superclass blueprint for all tiles  
    '''

    def __repr__(self) -> str:
        '''
        Returns machine-readable string used to construct identical instance
        of tile
        '''
        return f"{type(self).__name__}()"

    def __str__(self) -> str:
        '''
        Returns string character representing the type of tile
        '''
        return SYMBOLS[type(self).__name__]

    def get_tile_name(self) -> str:
        '''
        Returns string(name) of the specific class of the tile
        '''
        return type(self).__name__

    def is_blocking(self) -> bool:
        '''
        Returns True if the tile is blocking, by default tiles are not 
        blocking. 
        '''
        return False
    


class Ground(Tile):
    '''
    Subclass Ground tile
    '''
    pass



class Mountain(Tile):
    '''
    Subclass Mountain tile
    '''

    def is_blocking(self) -> bool:
        '''
        Returns True as mountains are unpassable terrain
        '''
        return True



class Building(Tile):
    '''
    Subclass Building tile
    '''

    def __init__(self, initial_health: int) -> None:
        '''
        Instantiates buliding with specified health 
        
        Parameters: 
        - initial_health: the initial health of the building 

        Precondition:
        - health will be between 0 and 9 inclusive 
        '''
        self.health = initial_health

    def __repr__(self) -> str:
        '''
        Returns machine-readable representation of a Buliding tile
        '''
        return f"{BUILDING_NAME}({self.health})"

    def __str__(self) -> str:
        '''
        Returns string interpretation of the building tile, which is
        the health 
        '''
        return str(self.health)

    def is_blocking(self) -> bool:
        '''
        Returns True only when the building is destroyed
        '''
        return not self.is_destroyed()

    def is_destroyed(self) -> bool:
        '''
        Returns True when the building is destroyed, False otherwise 
        '''
        return self.health == 0

    def damage(self, damage: int) -> None:
        '''
        Inflicts health change to a building
        Building cannot be healed above 9 health, or damaged below 0 health

        Parameters:
        - damage: the damage to be inflicted onto the building 
        '''
        self.health -= damage
        if self.health > MAX_BUILDING_HEALTH:
            self.health = MAX_BUILDING_HEALTH
        if self.health < 0:
            self.health = 0 



class Board():
    '''
    Superclass type for Board
    '''

    def __init__(self, board: list[list[str]]) -> None:
        '''
        Instantiates new board, given in str form, as well as another board 
        but in repr form

        Parameters:
        - board: a list of lists of strings with the tiles 

        Preconditions: 
        - each row within the board will have the same length
        - each board contains at least one row 
        - each character in the board is a valid __str__ representation of a 
        tile subclass described previously 
        '''
        self._initial_board = board
        self.board = []
        for row in board:
            board_row = []
            '''
            each character in the board is a row, each character in a
            row is a tile 
            ''' 
            for char in row:
                # converts symbol form to named() form 
                if char == MOUNTAIN_SYMBOL:
                    board_row.append(Mountain())
                elif char == GROUND_SYMBOL:
                    board_row.append(Ground())
                elif char == TILE_SYMBOL:
                    board_row.append(Tile())
                else:
                    board_row.append(Building(int(char)))
            self.board.append(board_row)

    def __repr__(self) -> str:
        '''
        Returns machine-readable representation of board
        '''
        return f"Board({self._initial_board})"

    def __str__(self) -> str:
        '''
        Returns string representation of board 
        '''
        strrep = ''
        for row in self._initial_board: 
            for char in row: 
                strrep += char 
            strrep += "\n"
        return strrep[:-1] # rid the extra "\n" at the end of the string 

    def get_dimensions(self) -> tuple[int, int]:
        '''
        Returns tuple consisting of the (#rows, #columns) of the board
        '''
        return (len(self.board), len(self.board[0])) 
        # amount of lists(rows) in board, amount of characters in a list

    def get_tile(self, position: tuple[int, int]) -> Tile:
        '''
        Returns the Tile at a sepecified position

        Parameters:
        - position: a tuple of the coordinates of the tile 

        Precondition:
        - provided position is not out of bounds
        '''
        row, col = position
        return self.board[row][col]

    def get_buildings(self) -> dict[tuple[int, int], Building]:
        '''
        Returns dictionary mapping the positions and instances of buildings
        '''
        buildings = {}
        for r_idx, row in enumerate(self.board):
            for c_idx, char in enumerate(row):
                if char.get_tile_name() == 'Building':
                    buildings[(r_idx, c_idx)] = char
        return buildings
    


class Entity():
    '''
    Superclass blueprint for all entities
    '''

    def __init__(
        self, 
        position: tuple[int, int], 
        initial_health: int, 
        speed: int, 
        strength: int) -> None:
        '''
        Instantiates new entity with specified attributes

        Parameters: 
        - position: a tuple of the coordinates of the Entity on the board
        - initial_health: initial health of the entity
        - speed: speed of the entity (integer)
        - strength: strength of the entity 
        '''
        self.position = position
        self.health = initial_health
        self.speed = speed
        self.strength = strength

    def __repr__(self) -> str:
        '''
        Returns machine-readable representation of entity traits 
        '''
        return f"{type(self).__name__}({self.position}, {self.health}, "\
            f"{self.speed}, {self.strength})"

    def __str__(self) -> str:
        '''
        Returns string-interpretation of entity traits
        '''
        return f"{SYMBOLS[type(self).__name__]},{self.position[0]},"\
            f"{self.position[1]},{self.health},{self.speed},{self.strength}"

    def get_symbol(self) -> str:
        '''
        Returns character symbol of the entity
        '''
        return SYMBOLS[type(self).__name__]

    def get_name(self) -> str:
        '''
        Returns the name of the specific entity class 
        '''
        return type(self).__name__

    def get_position(self) -> tuple[int, int]:
        '''
        Returns the (row, column) position of the entity
        '''
        return self.position

    def set_position(self, position: tuple[int, int]) -> None:
        '''
        Moves entity to specified position, changing position

        Parameters: 
        - position: tuple coordinates of the entity 
        '''
        self.position = position

    def get_health(self) -> int:
        '''
        Returns the integer health of the entity
        '''
        return self.health

    def get_speed(self) -> int:
        '''
        Returns the integer speed of the entity
        '''
        return self.speed

    def get_strength(self) -> int:
        '''
        Returns the integer strength of the entity
        '''
        return self.strength

    def damage(self, damage: int) -> None:
        '''
        Reduces the health of the entity

        Parameters:
        - damage: damage inflicted to the entity 
        '''
        if self.is_alive():
            self.health -= damage 
            if self.health < 0: 
            # health cannot dip below zero
                self.health = 0

    def is_alive(self) -> bool:
        '''
        Returns True if the entity if alive, False otherwise
        '''
        return self.health > 0

    def is_friendly(self) -> bool:
        '''
        Returns friendliness of entity, False by default 
        '''
        return False

    def get_targets(self) -> list[tuple[int, int]]:
        '''
        Returns a list of the positions of the available targets of the entity,
        by default this is 1 in every adjacent direction
        '''
        row, col = self.position
        return [(row, col + 1), (row, col - 1), (row + 1, col), (row - 1, col)]

    def attack(self, entity: "Entity") -> None:
        '''
        Attacks another entity, reducing their health by an amount equal to the
        attacking entity's strength

        Parameters: 
        - entity: entity that is to be attacked
        '''
        entity.damage(self.strength)
    


class Mech(Entity):
    '''
    Subclass Mech entity 

    Precondition:
    - Mech is always active upon instantiation
    '''

    def __init__(
        self, 
        position: tuple[int, int], 
        initial_health: int, 
        speed: int, 
        strength: int) -> None:
        '''
        Instantiates Mech with Mech attributes in addition to entity attributes

        Parameters: 
        - position: a tuple of the coordinates of the Mech on the board
        - initial_health: initial health of the Mech
        - speed: speed of the Mech (integer)
        - strength: strength of the Mech 
        '''
        super().__init__(position, initial_health, speed, strength)
        self.active = True
        self.previous_position = position

    def is_friendly(self) -> bool:
        '''
        Returns True since all Mechs are friendly 
        '''
        return True

    def set_position(self, position: tuple[int, int]) -> None:
        '''
        Sets position of Mech to any space

        Parameters: 
        - position: tuple coordinates of the position of the Mech
        '''
        self.previous_position = self.position
        self.position = position

    def enable(self) -> None:
        '''
        Enables Mech, used for evaluating the end of turns 
        '''
        self.active = True

    def disable(self) -> None:
        '''
        Disables Mech, used for evaluating the end of turns 
        '''
        self.active = False

    def is_active(self) -> bool:
        '''
        Returns True if Mech is enabled, False otherwise 
        '''
        return self.active
    


class TankMech(Mech):
    '''
    Subclass TankMech entity

    Attacks horizontally, with a horizontal radius of 5
    '''

    def get_targets(self) -> list[tuple[int, int]]:
        '''
        Returns a list of board coordinates that the TankMech targets
        '''
        row, col = self.position
        targets = []
        for attackable_range in range(1, TANK_RANGE + 1):
            '''
             - TankMech has a 5 horizontal range
             - range(1,6) gives integer values of how far left and right the 
               entity is able to target
            '''
            targets.append((row, col + attackable_range))
            targets.append((row, col - attackable_range))
        return targets
    


class HealMech(Mech):
    '''
    Subclass HealMech entity 

    Heals all entities in default (1) entity taxicab radius, given that they 
    are friendly and alive
    '''

    def get_strength(self) -> int:
        '''
        Changes strength attribute to inflict healing:
        
        Attack is equal to strength, thus damaging another entity 
        by NEGATIVE health 'heals' 
        '''
        return -self.strength

    def attack(self, unit) -> None:
        '''
        Overwritting entity attack method 

        Parameters:
        - unit: the unit (building or entity) that is being healed by the 
        HealMech
        '''
        if str(unit).isdigit() or unit.is_friendly():
            '''
            - healmech heals all target mechs and entities
            - building 'if' condition goes first since building friendliness 
            cannot be evaluated
            '''
            unit.damage(self.get_strength())



class Enemy(Entity):
    '''
    Subclass Enemy Entity 
    '''

    def __init__(
        self, 
        position: tuple[int, int], 
        initial_health: int, 
        speed: int, 
        strength: int) -> None:
        '''
        Instantiates Enemy 

        Parameters: 
        - position: a tuple of the coordinates of the Enemy on the board
        - initial_health: initial health of the Enemy
        - speed: speed of the Enemy (integer)
        - strength: strength of the Enemy 
        '''
        super().__init__(position, initial_health, speed, strength)
        # position also instantiated, relevant to objective allocation 
        self.objective = position

    def is_friendly(self) -> bool:
        '''
        Returns False since all Enemies are not friendly 
        '''
        return False

    def get_objective(self) -> tuple[int, int]:
        '''
        Returns current coordinates of the enemy's objective
        '''
        return self.objective

    def update_objective(self, entities: list[Entity], buildings: 
                         dict[tuple[int, int], Building]) -> None:
        '''
        Updates enemy objective based on current game state, default behaviour
        is to set objecctive to current position

        Parameters:
        - entities: list of entities 
        - buildings: dictionary of building coordinates and Buildings 
        '''
        self.objective = self.position



class Scorpion(Enemy):
    '''
    Subclass Scorpion enemy
    '''

    def get_targets(self) -> list[tuple[int, int]]:
        '''
        Returns list of board coordinates that are in the Scorpion's range
        Range is 2 in all directions 
        '''
        row, col = self.position
        targets = []
        for attackable_range in range(1, SCORPION_RANGE + 1):
            targets.extend([(row, col + attackable_range), 
                            (row, col - attackable_range), 
                            (row + attackable_range, col), 
                            (row - attackable_range, col)])
            # extends list of valid targets 
        return targets

    def update_objective(self, entities: list[Entity], 
                         buildings: dict[tuple[int, int], Building]) -> None:
        '''
        Overwrites update_objective inherited from Enemy Class 

        Scorpion attacks mechs with the highest health & highest priority

        Parameters:
        - entities: list of entities 
        - buildings: dictionary of building coordinates and Buildings 
        '''
        highest_health = -1  # ensure first (any) mech is the objective 
        new_objective = self.position
        for entity in entities:
            if entity.is_friendly() and entity.get_health() > highest_health:
                '''
                Objective is the first mech with the most health, thus >= 
                avoided
                '''
                highest_health = entity.get_health()
                new_objective = entity.get_position()

        if highest_health != -1:
            # elif no mechs alive, objective remains same 
            self.objective = new_objective

    

class Firefly(Enemy):
    '''
    Subclass Firefly enemy
    '''

    def get_targets(self) -> list[tuple[int, int]]:
        '''
        Returns list of board coordinates that are in the Firefly's range
        Range is 5 units above and below  
        '''
        row, col = self.position
        targets = []
        for i in range(1, FIREFLY_RANGE + 1):
            targets.extend([(row + i, col), (row - i, col)])
        return targets

    def update_objective(self, entities: list[Entity], 
                         buildings: dict[tuple[int, int], Building]) -> None:
        '''
        Overwrites update_objective inherited from Enemy Class 

        Firefly attacks the buildings closest to the bottom right of the board, 
        with the highest health 

        Parameters:
        - entities: list of entities 
        - buildings: dictionary of building coordinates and Buildings 
        '''
        lowest_health = float('inf') # ensure first building is objective
        new_objective = self.position 
        # if there are no buildings, default objective (original position)

        for position, building in buildings.items():
            if int(str(building)) <= lowest_health:
                '''
                Given the buildings dictionary is in order from 0,0 to the 
                right and bottommost row, column, <= used to update objective
                '''
                lowest_health = int(str(building)) # str(building) e.g. '6'
                new_objective = position

        if lowest_health != float('inf'):
            self.objective = new_objective



class BreachModel():
    """
    Models the logical state of a game of Into The Breach.
    """

    def __init__(self, board: Board, entities: list[Entity]) -> None:
        """
        Instantiates a new model class with the given board and entities.

        Parameters: 
        - board: current Board state
        - entities: list of alive entities in the game 

        Precondition: 
        - entities list contains at least 1 entity 
        """
        self.board = board
        self.entities = entities

    def __str__(self) -> str:
        """
        Returns the string representation of the model.
        """
        board_str = str(self.board)
        entities_str = '' # Accumulator 
        for ent in self.entities: 
            entities_str += str(ent) + "\n"
        return f"{board_str}\n\n{entities_str[:-1]}" # [:-1] rid's last "\n"

    def get_board(self) -> Board:
        """
        Returns the current board instance.
        """
        return self.board

    def get_entities(self) -> list[Entity]:
        """
        Returns the list of all entities in descending priority order.
        """
        return self.entities
    
    def has_won(self) -> bool:
        """
        Returns True iff the game is in a win state, or when all enemies are
        dead and there is at least one existing building and mech 
        """
        all_mechs_dead = True
        buildings = self.board.get_buildings()        
        if not (len(buildings) or len(self.entities)):
            # if there are no existing buildings or entities 
            return False
        
        for ent in self.entities:
            if not ent.is_friendly(): 
                # if entity is an enemy, game not won 
                return False
            all_mechs_dead = False
            
        for building in buildings.values():
            '''
            buildings.values() e.g: 
            [Building(5), Building(0), Building (3)]
            '''
            if not building.is_destroyed() and not all_mechs_dead: 
                # if there is alive building and all mechs aren't dead, won
                return True 
        return False 
        # in case there is a building but no alive enemies or mechs, False
        
    def has_lost(self) -> bool:
        """
        Returns True iff the game is in a loss state, or when either all 
        buildings or all mechs are destroyed 
        """
        all_buildings_destroyed = True
        all_mechs_dead = True 
        buildings = self.board.get_buildings()   

        if not (len(buildings) or len(self.entities)):
            # if there are no existing buildings or entities 
            return True 
        for coordinate in buildings.keys():
            if not self.get_board().get_tile(coordinate).is_destroyed(): 
                all_buildings_destroyed = False
        for ent in self.entities:
            if ent.is_friendly():
                all_mechs_dead = False 
        return all_buildings_destroyed or all_mechs_dead
        # if either are all buildings or mechs unalive, return True 
        
    def entity_positions(self) -> dict[tuple[int, int], Entity]:
        """
        Returns a dictionary of all entities, indexed by entity position
        """
        positions = {}
        for entity in self.entities: 
            positions[entity.get_position()] = entity
            # insert in dictionary the key(position) and it's value(entity)
        return positions

    def get_valid_movement_positions(self, 
                                     entity: Entity) -> list[tuple[int, int]]:
        """
        Returns a list of positions a given entity can move to.
        """
        rows, cols = self.board.get_dimensions()
        valid_positions = []

        for row in range(rows): 
            for col in range(cols):
                # iterate through all board tiles 
                coordinate = (row, col)
                distance = get_distance(self, entity.get_position(), 
                                        coordinate)
                '''
                If the tile has a distance to the entity that is equal to 
                or less than the entity, it is a valid movement position 
                '''
                if 0 < distance <= entity.get_speed():
                    # if coordinate throws -1, not a valid coordinate
                    valid_positions.append(coordinate)
        return valid_positions

    def attempt_move(self, entity: Entity, position: tuple[int, int]) -> None:
        """
        Moves the given entity to the specified position if the entity is 
        friendly, active, and the position is valid 

        Parameters: 
        - entity: Entity attempting to move 
        - position: position that the Entity is trying to move to 
        """
        if (entity.is_friendly() 
            and entity.is_active()
            and position in self.get_valid_movement_positions(entity)):
            entity.set_position(position)

            # Update the entity in the entities list
            for idx, ent in enumerate(self.entities):
                if ent == entity:
                    self.entities[idx] = entity
                    break
            entity.disable()

    def ready_to_save(self) -> bool:
        """
        Returns True only when no move has been made since the last call to 
        end turn.
        """
        for entity in self.entities:
            if entity.is_friendly() and not entity.is_active():
                # if any move is made, at least 1 mech is inactive 
                return False 
        return True 

    def assign_objectives(self) -> None:
        """
        Updates the objectives of all enemies based on the current game state.
        """
        buildings = self.board.get_buildings()
        for entity in self.entities:
            if not entity.is_friendly():
                # update every enemy's objective using existing method 
                entity.update_objective(self.entities, buildings)
            
    def move_enemies(self) -> None:
        """
        Moves each enemy closest to their objective, ensuring the position has 
        a valid path
        """
        for entity in self.entities: 
            if not entity.is_friendly():
                move_position = entity.get_position() 
                # don't move if there are no valid positions 
                closest_distance = float('inf')
                # ensure first valid movement is moved to (and distance not -1)
                for coordinate in self.get_valid_movement_positions(entity):
                    '''
                    For every enemy's valid positions, get its 
                    distance from the enemy's objective
                    '''
                    distance = get_distance(self, entity.get_objective(), 
                                                         coordinate) 
                    if distance <= closest_distance and distance != -1:
                        closest_distance = distance
                        '''
                        If the distance is less than the closest distance, 
                        update move position 
                        '''
                        move_position = coordinate 
                for idx, ent in enumerate(self.entities): 
                    # update entities list after setting each position
                    if ent == entity:
                        entity.set_position(move_position)
                        self.entities[idx] = entity
                        break

    def make_attack(self, entity: Entity) -> None:
        """
        Makes given entity perform an attack against every tile that is 
        currently a target of the entity

        Parameters:
        - entity: the entity that is making an attack 
        """
        targets = entity.get_targets()
        for tile in targets: 
            if tile in self.entity_positions():
                '''
                - if the target is an entity, attack it
                - if the attacked entity dies, remove it from the enities list 
                - if the attacked entity is still alive, update its health 
                '''
                attacked_entity = self.entity_positions()[tile]
                entity.attack(attacked_entity) 
                for idx, ent in enumerate(self.entities):
                    if ent.get_position() == tile:
                        if not attacked_entity.is_alive():
                            self.entities.remove(self.entities[idx])
                            break
                        self.entities[idx] = attacked_entity
                    
            if tile in self.board.get_buildings():
                '''
                - if the target is a building, attack it
                - update the board with the new building health 
                '''
                building = self.board.get_buildings()[tile]
                entity.attack(building)
                self.board.board[tile[0]][tile[1]] = building # update board 
                
    def end_turn(self) -> None:
        """
        Executes the attack and enemy movement phases, and then sets 
        all mechs to be active.
        """
        for entity in self.entities:
            self.make_attack(entity)
        self.assign_objectives()
        self.move_enemies()
        for entity in self.entities:
            if entity.is_friendly():
                entity.enable()



TILE_COLORS = {
    TILE_NAME: GROUND_COLOR,
    GROUND_NAME: GROUND_COLOR,
    MOUNTAIN_NAME: MOUNTAIN_COLOR,
    BUILDING_NAME: BUILDING_COLOR,
}

ENTITY_DISPLAYS = {
    TANK_NAME: TANK_DISPLAY, 
    HEAL_NAME: HEAL_DISPLAY,
    SCORPION_NAME: SCORPION_DISPLAY,
    FIREFLY_NAME: FIREFLY_DISPLAY
}

# helper dictionaries to minimise duplication 



class GameGrid(AbstractGrid):
    """
    A view component that displays the game board, with entities overlaid 
    on top.
    """
    def redraw(self, board: Board, entities: list[Entity], 
               highlighted: list[tuple[int, int]] = None, 
               movement: bool = False) -> None:
        """
        Clears the game grid, then redraws it according to the provided 
        information.

        Parameters: 
        - board: current Board state 
        - entities: list of alive entities currently in play
        - highlighted: list of coordinates that are highlighted (targets or 
        valid move positions)
        - movement: boolean describing if Mech is active or not 
        """
        self.clear()
        self.set_dimensions(board.get_dimensions())

        rows, cols = board.get_dimensions()
        for row in range(rows):
            for col in range(cols):
                '''
                - highlight highlighted cells 
                - set buildings colour and annotation 
                - colour cells appropriate tile colour 
                '''
                position = (row, col)
                tile = board.get_tile(position)
                if position in highlighted: 
                    self.color_cell(position, 
                                    MOVE_COLOR if movement else ATTACK_COLOR)
                    continue 
                elif position in board.get_buildings():
                    if tile.is_destroyed(): 
                        self.color_cell(position, DESTROYED_COLOR)
                        continue
                    self.color_cell(position, BUILDING_COLOR)
                    self.annotate_position(position, str(tile), ENTITY_FONT)
                    continue  
                self.color_cell(position, TILE_COLORS[tile.get_tile_name()])

        for entity in entities:
            # add entity annotation over tiles 
            self.annotate_position(entity.get_position(), 
                                   ENTITY_DISPLAYS[entity.get_name()], 
                                   ENTITY_FONT)
                
    def bind_click_callback(self, 
                            click_callback: Callable[[tuple[int, int]], 
                                                     None]) -> None:
        """
        Binds the <Button-1> and <Button-2> events on itself to a function that 
        calls the provided click handler at the correct position.
        
        Parameters: 
        - click_callback: a function that is called 
        """
        def handler(event):
            # gathers click position to call appropriate command in game 
            position = self.pixel_to_cell(event.x, event.y)
            click_callback(position)
        self.bind("<Button-1>", handler)
        self.bind("<Button-2>", handler)



class SideBar(AbstractGrid):
    """
    A view component that displays properties of each entity.
    """
    def __init__(self, master: tk.Widget, dimensions: tuple[int, int], 
                 size: tuple[int, int]) -> None:
        '''
        Instantiates SideBar 

        Parameters:
        - master: the container or window frame for the widget 
        - dimensions: the dimensions of the abstract grid 
        - size: tuple giving pixel size of the widget 
        '''
        super().__init__(master, dimensions, size)
        # inherits from AbstractGrid, dimensions, size 
        self._dimensions = dimensions
        self._size = size

    def display(self, entities: list[Entity]) -> None:
        """
        Clears the side bar, then redraws the header followed by the relevant 
        properties of the given entities.

        Parameters:
        - entities: list of entities currently in play (alive) 
        """
        self.clear()
        self._dimensions = (len(entities) + 1, 4)
        '''
        dimensions of SideBar is the entities alive (list), + 1 for 
        the header but always 4 columns for the entity, coordinate, 
        health and strength 
        '''
        for col, header in enumerate(SIDEBAR_HEADINGS):
            self.annotate_position((0, col), header, SIDEBAR_FONT)
            # annotate side bar 

        for row, entity in enumerate(entities):
            # annotate SideBar according to entities list 
            actual_row = row + 1
            symbol = ENTITY_DISPLAYS[entity.get_name()]
            position = entity.get_position()
            health = entity.get_health()
            strength = entity.get_strength()
            self.annotate_position((actual_row, 0), symbol, ENTITY_FONT)
            self.annotate_position((actual_row, 1), f"{position}", ENTITY_FONT)
            self.annotate_position((actual_row, 2), f"{health}", ENTITY_FONT)
            self.annotate_position((actual_row, 3), f"{strength}", ENTITY_FONT)



class ControlBar(tk.Frame):
    """
    A view component that contains three buttons that allow the user to 
    perform administration actions.
    """
    def __init__(self, master: tk.Widget, save_callback: 
                 Optional[Callable[[], None]] = None, 
                 load_callback: Optional[Callable[[], None]] = None, 
                 turn_callback: Optional[Callable[[], None]] = None, 
                 **kwargs) -> None:
        ''' 
        Instantiates control bar frame, to be packed into BreachView 

        Parameters:
        - master: containter of the widget
        - save_callback: save command function for button 
        - load_callback: load command function for button 
        - turn_callback: end turn function for the button 
        '''

        super().__init__(master, **kwargs)
        self.save_button = tk.Button(self, text=SAVE_TEXT, 
                                     command=save_callback)
        self.load_button = tk.Button(self, text=LOAD_TEXT, 
                                     command=load_callback)
        self.turn_button = tk.Button(self, text=TURN_TEXT, 
                                     command=turn_callback)

        self.save_button.pack(side=tk.LEFT, expand=True, padx=5)
        self.load_button.pack(side=tk.LEFT, expand=True, padx=5)
        self.turn_button.pack(side=tk.LEFT, expand=True, padx=5)



class BreachView:
    """
    The main view class that wraps around the smaller GUI components, 
    providing a single view interface for the controller.
    """
    def __init__(self, root: tk.Tk, board_dims: tuple[int, int], 
                 save_callback: Optional[Callable[[], None]] = None, 
                 load_callback: Optional[Callable[[], None]] = None, 
                 turn_callback: Optional[Callable[[], None]] = None) -> None:
        '''
        Instantiates BreachView, GUI for IntoTheBreach

        Parameters:
        - root: window
        - board_dims: dimensions of the play board 
        - save_callback: save command function 
        - load_callback: load command function 
        - turn_callback: end turn function 
        '''
        self.root = root
        self.root.title(BANNER_TEXT)
        # name the game window the banner text 

        # pack banner
        self.banner = tk.Label(root, text=BANNER_TEXT, font=BANNER_FONT)
        self.banner.pack(fill=tk.X)

        # container frame for all other frames, widgets 
        self.container = tk.Frame(root)
        self.container.pack(fill=tk.BOTH, expand=True)

        # pack game board into container frame
        self.game_grid = GameGrid(self.container, dimensions=board_dims, 
                                  size=(GRID_SIZE, GRID_SIZE))
        self.game_grid.pack(side=tk.LEFT, padx=(0, 10), fill=tk.BOTH, 
                            expand=True)

        # pack side bar into containter frame
        self.side_bar = SideBar(self.container, dimensions=(0,0), 
                                size=(SIDEBAR_WIDTH, GRID_SIZE))
        self.side_bar.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # pack control bar at the bottom of the container 
        self.control_bar = ControlBar(root, save_callback=save_callback, 
                                      load_callback=load_callback, 
                                      turn_callback=turn_callback)
        self.control_bar.pack(fill=tk.X, pady=(10, 0))

    def bind_click_callback(self, click_callback: Callable[[tuple[int, int]], 
                                                           None]) -> None:
        """
        Binds a click event handler to the instantiated GameGrid based on 
        click callback.

        Parameters:
        - click_callback: a function that is called 
        """
        self.game_grid.bind_click_callback(click_callback)

    def redraw(self, board: Board, entities: list[Entity], 
               highlighted: list[tuple[int, int]] = None, 
               movement: bool = False) -> None:
        """
        Redraws the instantiated GameGrid and SideBar based on the given board, 
        list of entities, and tile highlight information.

        Parameters: 
        - board: current Board state 
        - entities: current entities that are in play, alive 
        - highlighted: highlighted squares on the board 
        - movement: boolean for if Mech has moved or not 
        """
        self.game_grid.redraw(board, entities, highlighted, movement)
        self.side_bar.display(entities)
        # redraw the board and update SideBar according to new game state



class IntoTheBreach:
    """
    The controller class for the overall game.
    """
    def __init__(self, root: tk.Tk, game_file: str) -> None:
        """
        Instantiates the controller. Creates instances of BreachModel and 
        BreachView, and redraws display to show the initial game state.

        Starts game: loads game file, window, reads game_file and redraws 
        the board

        Parameters:
        - root: window 
        - game_file: game file for the level to be loaded 
        """
        self.file = game_file 
        self.root = root
        self.model = self.load_model(game_file)
        self.view = BreachView(root, self.model.get_board().get_dimensions(), 
                               self.save_game, self.load_game, self.end_turn)
        self.view.bind_click_callback(self.handle_click)
        self.focussed_entity = None
        self.redraw()

    def load_model(self, file_path: str) -> BreachModel:
        """
        Replaces the current game state with a new state based on the provided 
        file. 

        Loads the BreachModel simultaneously 

        Parameters:
        - file_path: file path of the file (level) played 
        """
        with open(file_path, 'r') as file:
            lines = file.readlines()
            # load and read given file, 'with' automatically closes file 

        # accumulate board and entity lines 
        board_lines = []
        entity_lines = []
        reading_entities = False

        for line in lines:
            line = line.strip() # rid uniterable '\n' strings 
            if line == '':
                '''
                when a line that contains only '' is read, board is finished 
                and next lines are entity lines
                '''
                reading_entities = True
                continue
            if reading_entities:
                # if lines are being read 
                entity_lines.append(line)
            else:
                # append board lines
                board_lines.append(list(line))

        board = Board(board_lines)
        entities = []
        for entity_line in entity_lines:
            '''
            make entity list according to what was read from the file
            - for each entity line, first character is entity symbol, then 
            position, health, speed and strength 
            '''
            attribute = entity_line.split(',') 
            # makes each character in the line indexable []
            entity_type = attribute[0]
            position = (int(attribute[1]), int(attribute[2]))
            health = int(attribute[3])
            speed = int(attribute[4])
            strength = int(attribute[5])
            if entity_type == TANK_SYMBOL:
                entities.append(TankMech(position, health, speed, strength))
            elif entity_type == HEAL_SYMBOL:
                entities.append(HealMech(position, health, speed, strength))
            elif entity_type == SCORPION_SYMBOL:
                entities.append(Scorpion(position, health, speed, strength))
            elif entity_type == FIREFLY_SYMBOL:
                entities.append(Firefly(position, health, speed, strength))

        return BreachModel(board, entities)

    def redraw(self) -> None:
        """
        Redraws the view based on the state of the model and the current 
        focused entity.
        """
        highlighted = []
        # shows move positions, attack positions 
        movement = False
        # to distinguish between highlighting attack or movement tiles 

        if self.focussed_entity:
            '''
            - focussed entity is the entity that is clicked 
            - mech activity (is active()) changes according to if a mech has
            moved.
            - if mech clicked and mech active, highlighted = valid move 
            positions 
            - if mech clicked and mech inactive (already moved), highlighted = 
            targets 
            - if enemy clicked, highlighted = targets
            '''
            if self.focussed_entity.is_friendly():
                if self.focussed_entity.is_active():
                    highlighted = (self.model.get_valid_movement_positions
                                   (self.focussed_entity))
                    movement = True
                else:
                    highlighted = self.focussed_entity.get_targets()
            else:
                highlighted = self.focussed_entity.get_targets()

        self.view.redraw(self.model.get_board(), self.model.get_entities(), 
                         highlighted, movement)
            # redraw board according to new focussed entity, highlighted

    def set_focussed_entity(self, entity: Optional[Entity]) -> None:
        """
        Sets the given entity to be the one on which to base highlighting. 
        Or clears the focussed entity if None is given.

        Parameters:
        - entity: entity that is to be set focussed 
        """
        self.focussed_entity = entity
        self.redraw()

    def make_move(self, position: tuple[int, int]) -> None:
        """
        Attempts to move the focussed entity to the given position, and then 
        clears the focussed entity.

        Parameters:
        - position: position of the entity to be moved to 
        """
        if self.focussed_entity and self.focussed_entity.is_friendly():
            # move mech if after focussed (clicked), attempt move auto sorts 
            # if mech is active 
            self.model.attempt_move(self.focussed_entity, position)
            self.set_focussed_entity(None)
            # reset focussed entity 

    def save_game(self) -> None:
        """
        Saves the current game state to a file if no move has been made since t
        he last end turn.
        """
        if self.model.ready_to_save():
            file_path = filedialog.asksaveasfilename(
                defaultextension='.txt', filetypes=[('Text files', '*.txt')])
            if file_path:
                try:
                    with open(file_path, 'w') as file:
                        # construct the game state string
                        game_state = self.construct_game_state()
                        # write new file with the game state 
                        file.write(game_state)
                except IOError as e:
                    # send error if game not saved 
                    print(f"Error saving game: {e}")
                    messagebox.showerror(IO_ERROR_TITLE, 
                                         IO_ERROR_MESSAGE + file_path)
        else:
            # if not ready to save, show error 
            messagebox.showerror(INVALID_SAVE_TITLE, INVALID_SAVE_MESSAGE)
            print("Save attempt failed: not ready to save")

    def construct_game_state(self) -> str:
        """
        Constructs the game state string, including the board and entities. 

        Helper function for saving game, as self.model updates entities but 
        buildings remain the same
        """
        board_str = '' # accumulate board 
        board = self.model.get_board()
        rows, cols = board.get_dimensions()

        for row in range(rows):
            for col in range(cols):
                tile = board.get_tile((row, col))
                board_str += str(tile)
            board_str += '\n'
            # '\n' splits board and entities 

        entities_str = '' # accumulate entities 
        for entity in self.model.get_entities():
            entities_str += str(entity) + '\n'

        # combine board and entities 
        game_state = board_str + '\n' + entities_str.strip()
        return game_state

    def load_game(self) -> None:
        """
        Loads a game state from a file and replaces the current game state.
        """
        file_path = filedialog.askopenfilename(
            filetypes=[('Text files', '*.txt')])
        if file_path:
            # try to load new game state, send error if invalid file 
            try:
                self.model = self.load_model(file_path)
                self.set_focussed_entity(None)
                self.redraw()
            except IOError:
                messagebox.showerror(IO_ERROR_TITLE, 
                                     IO_ERROR_MESSAGE + file_path)

    def end_turn(self) -> None:
        """
        Executes the attack phase, enemy movement phase, and termination 
        checking.
        """
        self.model.end_turn()
        self.redraw()
        if self.model.has_won():
            if messagebox.askyesno("Victory", "You Win! " + PLAY_AGAIN_TEXT):
                self.restart_game()
            else:
                self.root.destroy()
        elif self.model.has_lost():
            if messagebox.askyesno("Defeat", "You Lost! " + PLAY_AGAIN_TEXT):
                self.restart_game()
            else:
                self.root.destroy()

    def restart_game(self) -> None:
        """
        Restarts the game from the initial game file.
        """
        self.model = self.load_model(self.file) 
        self.set_focussed_entity(None)
        self.redraw()

    def handle_click(self, position: tuple[int, int]) -> None:
        """
        Handler for a click from the user at the given (row, column) position.

        Parameters:
        - position: position on ther board where click occurred 
        """
        entity = self.model.entity_positions().get(position)

        if self.focussed_entity:
            if (self.focussed_entity.is_friendly() 
                and self.focussed_entity.is_active()):
                if (position in self.model.get_valid_movement_positions
                                                    (self.focussed_entity)):
                    '''
                    If an active mech has already been clicked, and a valid 
                    position is clicked, move mech and redraw board
                    '''
                    self.model.attempt_move(self.focussed_entity, position)
                    self.set_focussed_entity(None)
                    self.redraw()
                    return
                else:
                    # if not a valid position, unhighlight squares 
                    self.set_focussed_entity(None)
        if entity:
            # if entity not yet clicked, update focussed entity 
            self.set_focussed_entity(entity)
        else:
            # else unhighlight all, set focussed entity None
            self.set_focussed_entity(None)

        # always redraw to updated current game state 
        self.redraw()



def play_game(root: tk.Tk, file_path: str) -> None:
    """
    Starts the game.

    Parameters:
    - root: window for the game 
    - file_path: path of the level of the game to be played 
    """
    IntoTheBreach(root, file_path)
    root.mainloop()



def main() -> None:
    """
    The main function for running the game.
    """
    file_path = filedialog.askopenfilename()
    root = tk.Tk()
    play_game(root, file_path)

if __name__ == "__main__":
    main()
