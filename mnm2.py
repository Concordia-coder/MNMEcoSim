import numpy as np
from numpy.typing import NDArray
import sys

class Game:
    
    GOLD, FOOD, METAL, MANA, OIL, CRYSTAL, SUBDOLAK = range(7)

    RESOURCE_NAMES = (
        'Gold',
        'Food',
        'Metal',
        'Mana',
        'Oil',
        'Crystal',
        'Subdolak'
    )

    # Mines
    MINE_PURCHASE_COST_VALS = [6, 10, 13, 16, 23, 27, 31]
    MINE_FOOD_PURCHASE_COST = np.array((10, 0, 0, 0, 0, 0, 0))
    MINE_BASE_INCOMES = np.diag((6, 1, 1, 5, 1, 1, 1))
    MINE_BASE_GOLD_UPGRADE_COST = np.array((10, 10, 10, 6, 10, 10, 10))
    MINE_GOLD_UPGRADE_COSTS_MANA = (6, 10, 16, 23, 31) # For mana mine
    MINE_GOLD_UPGRADE_COSTS_DEFAULT = (10, 16, 23, 31) # For non-mana mines     
    MINE_RARE_UPCGRADE_COSTS = (0, 7, 7, 18, 5, 5, 5)
    
    mine_configs = np.array(( # Modify as needed
        (GOLD, 1),
        (FOOD, 1),
        (METAL, 1),
        (MANA, 1),
        (OIL, 1),
        (CRYSTAL, 1),
        (SUBDOLAK, 1),
        (GOLD, 2),
        (FOOD, 2),
        (METAL, 2),
        (MANA, 2),
        (OIL, 2),
        (CRYSTAL, 2),
        (SUBDOLAK, 2),
        (GOLD, 3),
        (FOOD, 3),
        (METAL, 3),
        (MANA, 3),
        (OIL, 3),
        (CRYSTAL, 3),
        (SUBDOLAK, 3),
        (GOLD, 4),
        (FOOD, 4),
        (METAL, 4),
        (MANA, 4),
        (OIL, 4),
        (CRYSTAL, 4),
        (SUBDOLAK, 4),
        (GOLD, 5),
        (FOOD, 5),
        (METAL, 5),
        (MANA, 5),
        (OIL, 5),
        (CRYSTAL, 5),
        (SUBDOLAK, 5)
    ))

    num_mines = mine_configs.shape[0]

    mines = np.zeros((num_mines, 17), dtype=np.float32)
    mines[:, 0:2] = mine_configs
    mines[:, 10:] = MINE_BASE_INCOMES[mines[:,0].astype(np.int32)]

    # Mine ID, mine type, mine owned, upgrade resource, upgrade costs (7)

    # Help 
    mine_upgrades = np.zeros((num_mines*7, 11))

    for num, mine in enumerate(mines):
        mine_upgrades[7*num:7*num+7,0] = num
        mine_upgrades[7*num:7*num+7,1] = mine[0]
        mine_upgrades[7*num:7*num+7,2] = 0
        mine_upgrades[7*num:7*num+7,3] = [0,1,2,3,4,5,6]
        mine_upgrades[7*num,4] = MINE_BASE_GOLD_UPGRADE_COST[int(mine[0])] # dufferebt fir nabas
        mine_upgrades[7*num+1,5] = 7
        mine_upgrades[7*num+2,6] = 7
        mine_upgrades[7*num+3,7] = 18
        mine_upgrades[7*num+4,8] = 5
        mine_upgrades[7*num+5,9] = 5
        mine_upgrades[7*num+6,10] = 5

    # Sends
    SEND_CONFIG = (
        (1, 0.7, 0, 3, 0, 0, 0, 0, 0),
        (1, 0.6, 0, 0, 3, 0, 0, 0, 0),
        (1, 0.7, 0, 0, 0, 9, 0, 0, 0),
        (5, 2.5, 0, 9, 0, 0, 0, 0, 0),
        (5, 2.2, 0, 0, 9, 0, 0, 0, 0),
        (5, 2.2, 0, 0, 0, 26, 0, 0, 0),
        (6, 1.5, 0, 0, 0, 0, 5, 0, 0),
        (6, 1.5, 0, 0, 0, 0, 0, 5, 0),
        (6, 1.5, 0, 0, 0, 0, 0, 0, 5),
        (7, 4.4, 0, 0, 0, 0, 7, 7, 0),
        (7, 4.4, 0, 0, 0, 0, 7, 0, 7),
        (7, 3.8, 0, 0, 0, 0, 0, 7, 7),
        (10, 5.5, 0, 18, 0, 0, 0, 0, 0),
        (10, 4.8, 0, 0, 18, 0, 0, 0, 0),
        (10, 5.5, 0, 0, 0, 50, 0, 0, 0),
        (17, 7, 0, 25, 0, 12, 0, 0, 0),
        (17, 7, 0, 0, 25, 12, 0, 0, 0),
        (17, 7, 0, 0, 0, 10, 20, 0, 0),
        (17, 7, 0, 0, 0, 10, 0, 20, 0),
        (17, 7, 0, 0, 0, 20, 0, 0, 20)
    )

    SEND_NAMES = (
        'Fat Ling', 
        'Acid Ling',
        'Drone Ling', 
        'Zealot', 
        'Marine', 
        'Slime', 
        'Mechanical Ling', 
        'Pink Crystaling', 
        'Scorpion',
        'Laserbot',
        'Hellion', 
        'Pink Crystalisk', 
        'Roach', 
        'Dark Reaper', 
        'Queen', 
        'Lurker', 
        'Mutalisk', 
        'Mule', 
        'Diamonster',
        'Voidray', 
    )

    sends = np.array(SEND_CONFIG, dtype=np.float32)

    # Units
    UNIT_CONFIGS = (
        (0, 0, 91, 55, 0, 0, 0, 0, 5, 140, 40, 0, 30, 0, 0, 5, 150, 50, 0, 40, 0, 0, 10), 
        (0, 0, 128, 0, 57, 0, 0, 0, 5, 110, 0, 25, 30, 0, 5, 5, 110, 0, 15, 30, 0, 10, 10),
        (0, 0, 150, 0, 0, 120, 0, 0, 10, 60, 0, 0, 60, 0, 0, 4, 100, 0, 0, 110, 0, 0, 10),
        (0, 0, 157, 0, 40, 0, 56, 0, 5, 148, 0, 20, 0, 20, 5, 5, 176, 0, 20, 0, 20, 5, 5)   
    )

    units = np.array(UNIT_CONFIGS, dtype=np.float32)

    UNIT_NAMES = ( # Need to double check these costs
        'Anubis',
        'Sun Idol',
        'Conjurer',
        'Robotron'
    )

    action_space = None
    action_dict = None

    def action_space_generator(units, sends, mines):
        return ((0,()), (1,())) + (
            tuple((2, (unit_id,)) for unit_id in range(len(units))) +
            tuple((3, (unit_id,)) for unit_id in range(len(units))) +
            tuple((4, (send_id,)) for send_id in range(len(sends))) +
            tuple((5, (mine_id,)) for mine_id in range(len(mines))) +
            tuple((6, (mine_id, res_id)) for res_id in range(7) for mine_id in range(len(mines)))
        )
    
    action_space = action_space_generator(units, sends, mines)
    action_dict = {element: index for index, element in enumerate(action_space)}

    def __init__(self, mines: NDArray, mine_upgrades: NDArray, sends: NDArray, units: NDArray):

        self.bank = np.array((60, 0, 0, 0, 0, 0, 0), dtype=np.float32) # Start with 60 gold.
        self.income = np.array((16, 0, 0, 0, 0, 0, 0), dtype=np.float32) # Start with +16 gold income.
        self.round = 1 # Start on round 1.
        self.const = 1 # Start with 1 construction yard.
        self.const_cost = np.array((31, 0, 0, 0, 0, 0, 0))
        self.units = units.copy()
        self.sends = sends.copy()
        self.mines = mines.copy()
        self.owned_mines = 0
        self.mine_purchase_cost = np.array((Game.MINE_PURCHASE_COST_VALS[0], 0, 0, 0, 0, 0, 0), dtype=np.float32)
        self.mine_upgrades = mine_upgrades.copy()
        self.action_space = Game.action_space
        self.action_dict = Game.action_dict
        self.actions_available = self.get_available_actions()
        self.moves_performed = []
        self.action_types = (
            self.next_round,
            self.purchase_const,
            self.purchase_unit,
            self.upgrade_unit,
            self.purchase_send,
            self.purchase_mine,
            self.upgrade_mine
        )
      
    def __str__(self):
        return f'Round {self.round}. Bank: {self.bank}, Income +{self.income}' 

    # General
    def get_score(self):
        return np.sum(self.units[:,0]) + 10*np.sum(self.units[:,1])

    def affordable(self, costs):
        if costs.ndim == 1:
            return np.all((self.bank - costs) >= 0)
        else:
            return np.all((self.bank - costs) >= 0, axis=1)

    # Round
    def next_round(self): # Main action 0 
        self.bank += self.income
        self.round += 1
        return f"-> Proceeding to round {self.round}"
    
    def get_next_round(self):
        return ((0,()),)

    # Construction Yard
    def purchase_const(self): # Main action 1
        self.bank -= self.const_cost
        self.const_cost[0] += 10
        self.const += 1
        return f"-> Built construction yard {self.const}"  
    
    def const_affordable(self):
        if self.affordable(self.const_cost):
            return ((1,()),)
        else:
            return ()

    # Units
    def purchase_unit(self, unit_id): # Main action 2
        cost = self.units[unit_id, 9:16]
        if np.sum(self.units[unit_id, :2]) == 0: # Need to research
            cost += self.units[unit_id, 2:9] 
        self.bank -= cost            
        self.units[unit_id, 0] += 1
        return f"-> Purchased unit {Game.UNIT_NAMES[unit_id]}"
    
    def get_purchasable_units(self): # Needs to be affordable. Returns tuple of actions?
        need_to_research = np.sum(self.units[:, :2], axis=1) == 0
        costs = np.empty((self.units.shape[0], 7))
        costs[need_to_research] = self.units[need_to_research, 2:9] + self.units[need_to_research, 9:16]
        costs[~need_to_research] = self.units[~need_to_research, 9:16]
        affordable_units = self.affordable(costs)
        affordable_units_indices = np.nonzero(affordable_units)[0]
        return tuple((2, (unit_id,)) for unit_id in affordable_units_indices)
    
    def upgrade_unit(self, unit_id): # Main action 3
        unit = self.units[unit_id]
        cost = unit[16:]
        self.bank -= cost
        unit[0] -= 1
        unit[1] += 1
        return f"-> Upgraded unit {Game.UNIT_NAMES[unit_id]}"
    
    def get_upgradable_units(self): # Needs to have at least one unupgraded and affordable. Returns tuple of actions?
        have_base_unit = self.units[:, 0] > 0
        costs = self.units[have_base_unit, 16:]
        affordable_upgrades = self.affordable(costs)
        affordable_upgrades_indices = np.nonzero(affordable_upgrades)[0]
        return tuple((3, (unit_id,)) for unit_id in affordable_upgrades_indices)

    # Sends
    def purchase_send(self, send_id): # Main action 4
        self.bank -= self.sends[send_id,2:]
        self.income[0] += self.sends[send_id,1] 
        return f"-> Purchased send {Game.SEND_NAMES[send_id]}"
    
    send_indices = np.arange(sends.shape[0])
    def get_purchasable_sends(self): 
        # Filter for available sends
        available_mask = self.sends[:,0] <= self.round
        available_sends = self.sends[available_mask]
        available_indices = Game.send_indices[available_mask]

        # Filter for affordable sends
        affordable_sends_mask = self.affordable(available_sends[:,2:])
        affordable_indices = available_indices[affordable_sends_mask]

        # Create and return the tuple of actions
        return tuple((4, (send_id,)) for send_id in affordable_indices)  

    # Mines
    def purchase_mine(self, mine_id): # Main action 5
        self.mines[mine_id, 2] = 1 # Set mine to owned (1 = true, 0 = false)
        if self.mines[mine_id,0] == Game.FOOD: 
            self.bank[0] -= 10
        else:
            if self.owned_mines <= 6:
                self.mine_purchase_cost[0] = Game.MINE_PURCHASE_COST_VALS[self.owned_mines]
            self.bank[0] -= self.mine_purchase_cost[0]
            self.owned_mines += 1

        self.income += self.mines[mine_id,10:]
        self.mine_upgrades[7*mine_id:7*mine_id+7,2] = 1
        return f"-> Purchased {Game.RESOURCE_NAMES[int(self.mines[mine_id,0])]} mine (ID {mine_id})"
    
    # MINE_PURCHASE_COST_VALS
    mine_indices = np.arange(mines.shape[0])
    def get_purchasable_mines(self):
        # Filter for available mines
        available_mask = (self.mines[:, 2] == 0) & (self.mines[:, 1] <= self.const)
        available_indices = Game.mine_indices[available_mask]

        # Filter for affordable sends
        costs = np.zeros((self.mines.shape[0], 7))
        food_mines = self.mines[:, 0] == Game.FOOD
        costs[food_mines] = Game.MINE_FOOD_PURCHASE_COST  # set cost for food mines
        costs[~food_mines] = self.mine_purchase_cost  # set cost for non-food mines        
        
        affordable_mines = self.affordable(costs[available_indices])
        affordable_indices = available_indices[affordable_mines]

        # Create and return the tuple of actions
        return tuple((5, (mine_id,)) for mine_id in affordable_indices) 

    def upgrade_mine(self, mine_id, res_id): # Main action 6
        mine = self.mines[mine_id]
        mine_type = int(mine[0])
        mine_upgrades_index = 7*mine_id+res_id
        
        old_income = mine[10:].copy()
        mine[3+res_id] += 1
        mine_upgrade_val = int(mine[3+res_id])
        cost = self.mine_upgrades[mine_upgrades_index,4:11]
        self.bank -= cost
        
        if res_id > 0:
            self.mine_upgrades[mine_upgrades_index,2] = 0
        else:
            if mine_type == 3:
                if mine_upgrade_val > 4:
                    self.mine_upgrades[mine_upgrades_index,2] = 0
                else:
                    self.mine_upgrades[mine_upgrades_index,4] = Game.MINE_GOLD_UPGRADE_COSTS_MANA[mine_upgrade_val] 
            else:
                if mine_upgrade_val > 3:
                    self.mine_upgrades[mine_upgrades_index,2] = 0
                else:
                    self.mine_upgrades[mine_upgrades_index,4] = Game.MINE_GOLD_UPGRADE_COSTS_DEFAULT[mine_upgrade_val]
        
        mine[10+mine_type] = np.round((Game.MINE_BASE_INCOMES[mine_type,mine_type] + mine[3]) * (1 + 0.2*np.sum(mine[4:10])), 1)
        
        delta_income = mine[10:] - old_income
        self.income += delta_income

        return f"-> Upgraded {Game.RESOURCE_NAMES[mine_type]} mine (ID {mine_id}) with {Game.RESOURCE_NAMES[res_id]}"
    
    mine_upgrade_indices = np.arange(mine_upgrades.shape[0])
    def get_upgradable_mines(self): 
        # Filter for available upgrades
        available_mask = self.mine_upgrades[:,2] == 1
        available_upgrades = self.mine_upgrades[available_mask]
        available_indices = Game.mine_upgrade_indices[available_mask]

        # Filter for affordable upgrades
        costs = available_upgrades[:,4:]
        affordable_mines_mask = self.affordable(costs)
        affordable_indices = available_indices[affordable_mines_mask]

        # Create and return the tuple of actions
        return tuple((6, (int(self.mine_upgrades[i, 0]), int(self.mine_upgrades[i, 3]))) for i in affordable_indices)
    
    def get_available_actions(self):
        """
        Updates self.available_moves with a list of all the possible valid moves.
        """
        action_tuples = self.get_next_round() + self.const_affordable() + self.get_purchasable_units() + self.get_upgradable_units() + self.get_purchasable_sends() + self.get_purchasable_mines() + self.get_upgradable_mines()
        return tuple(
            self.action_dict[action] 
            for action in action_tuples 
        )
    
    def action_int_to_text(self, action_int):
        #print(action_int, self.action_space[action_int])
        return self.action_tuple_to_text(self.action_space[action_int])
    
    def action_tuple_to_text(self, action_tuple):
        #print(action_tuple)
        if action_tuple[0] == 0:
            return 'Next round.'
        elif action_tuple[0] == 1:
            return f'Purchase construction yard {self.const+1}'
        elif action_tuple[0] == 2:
            return f'Purchase {Game.UNIT_NAMES[action_tuple[1][0]]}'
        elif action_tuple[0] == 3:
            return f'Upgrade {Game.UNIT_NAMES[action_tuple[1][0]]}'
        elif action_tuple[0] == 4:
            return f'Purchase {Game.SEND_NAMES[action_tuple[1][0]]}'
        elif action_tuple[0] == 5:
            return f'Purchase {Game.RESOURCE_NAMES[int(self.mines[action_tuple[1][0],0])]} Mine.'
        elif action_tuple[0] == 6:
            return f'Upgrade +{self.mines[action_tuple[1][0],10+int(self.mines[action_tuple[1][0],0])]} {Game.RESOURCE_NAMES[int(self.mines[action_tuple[1][0],0])]} Mine with {Game.RESOURCE_NAMES[action_tuple[1][1]]}.'
 

    def input_action(self):
        """
        Human interface to the game. Accepts a move.
        """
        while True: # Keep looping until we get a valid move.
            user_input = input("Choose your action or type exit: ")
            if user_input.lower() == 'exit': # End game if type exit.
                print("Exiting game.")
                exit()
            try: 
                user_input = int(user_input) # Get the user's input and try to cast it as an integer.
                if user_input in self.actions_available: # See if it's in the range of valid moves.
                    return user_input # If it is, return it.
                else: # Not a valid move, try again.
                    print(f"Please enter a valid integer move.")
            except ValueError: # Not an int, try again.
                print(f"Please enter a valid integer move.")


    def perform_action(self, action_num):
        """
        Performs a valid move from self.available_moves.
        """
        action_tuple = self.action_space[action_num]
        func, args = action_tuple  # Figure out which method to call with which arguments.
        result = self.action_types[func](*tuple(args)) # If the method has args pass them, otherwise just call the method.
        self.moves_performed.append(result) # Log the move.
        return result


    def play_match(self):
        """
        Implements a human interface to play a full game. Keeps looping until end of round 37 or player types exit.
        """
        print(str(self)) # Print initial bank/income/etc.
        while self.round < 38: # Keep playing until we reach end of round 37.
            for possible_action in self.actions_available:
                print(f'{possible_action}: {self.action_int_to_text(possible_action)}')
            action = self.input_action() # Ask for an action.
            confirmation = self.perform_action(action) # Perform the action.
            print(confirmation) # Print the action
            print(str(self)) # After the action print the new bank/income/etc.
            self.actions_available = self.get_available_actions() # Update available moves.
        print(f"---> Game complete! Finished game with bank: {self.bank}, income: {self.income}!") # Print the final bank/income.
        
    def get_state(self):
        return np.concatenate((self.bank, self.income, np.array([self.round])))

    
def main():
    while True: # Keep playing games until player exists.
        print("Starting new game!") 
        gs = Game(Game.mines, Game.mine_upgrades, Game.sends, Game.units)
        gs.play_match() # Play the game.

        play_again = input("Do you want to play again? (y/n): ") 
        if play_again.lower() != 'y': # If they don't want to play anymore
            print("Thanks for playing!")
            break # Exit.


if __name__ == "__main__":
    sys.exit(main())