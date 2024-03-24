"""
Author: Justin Goodrich
Version: 0.1
Date: 3-24-2024

This is mnm.py, a Python project that implements a basic model of the economy of StarCraft II arcade game Mines and Magic ( https://sc2arcade.com/map/1/223843/ )

Mines and Magic is a round-based, 4v4 squadron defense game with a complex economy. Each round the player decides whether to build new or upgrade existing army units, build new or upgrade existing "mines" on resource nodes, buy "sends" which attack the enemy and also provide income, or build more "construction yards" which increases the number of resource nodes on the map that are accessible for mining.

The economy consists of one main resource (gold) and six secondary resources (food, metal, mana, oil, crystal, and subdolak). All units require some gold and at least one type of secondary resource to construct. You start with a small base income of gold and accessible but unowned resource nodes available to build. Nodes representing all seven resources are available. The first mine only costs a small amount of gold to construct, but subsequent mines become more gold expensive, to a cap. Mines can also be upgraded 4 to 5 times with gold, and can be upgraded once with each of the secondary resources to increase its yield by 20%.

For example, an unupgraded metal mine gives +1 metal/round. Buying 2 gold upgrades brings it up to +3 metal/round, and then investing food, metal, and oil into the mine gives it an extra 60% yield, so it would give +4.8 metal/round. With max upgrades, most mines can give up to +11 resource/turn, except for gold and mana mines, which can go up to +22 resource/turn.

Furthermore, sends can be purchased with the secondary resources, which provide permenant gold income/round. For example, a "Mule" can be sent with 20 oil and 10 mana, which then provides +8 gold/turn. There is a balance between upgrading mines for the +20% bonus with secondary resources and sending to provide base gold income.

When playing "normally", you build armies with your banked resources and get bonus gold for clearing all of the AI minions that spawn each wave before then spending excess resources on mines and sends - essentially attempting to build the "smallest army possible" which clears the enemy waves but leaves resources left over for reinvestment. However, since Mines and Magic is a team game, a viable strategy called "ecoing" is to not build any units, forgoing the bonus gold income from killing, but instead re-investing all of your resources into your economy through the midgame in an attempt to maximize your economy from mining and sending. You only start to build units in the lategame after your economy has completely ballooned. In this strategy, you rely on your allies to kill the mobs spawned against you so that you don't lose the game by having your team's fortress destroyed. 

After the last round, your team's joint army faces off against the opposing team's joint army for the win. 

The ultimate goal of this project is to attempt to find the optimal or at least very strong "eco" strategies that maximize the number of units available at the end of the game.  

TO DO:
- Better model the eco early game by giving bonus gold income through first 6-7 rounds. (Normally people who eco build a few units early so they get the bonus gold income from the early game before "selling" those units around wave 6 or 7.)
- Add ability to build late game units and assign some score or metric to the end of the game based off how many exist.
- Modify API to interface with model to train.
- Performance improvements.
- ??
"""

import numpy as np
import sys
import copy

### Information about the resources
GOLD, FOOD, METAL, MANA, OIL, CRYSTAL, SUBDOLAK = range(7)

resource_names = {
    GOLD: 'Gold',
    FOOD: 'Food',
    METAL: 'Metal',
    MANA: 'Mana',
    OIL: 'Oil',
    CRYSTAL: 'Crystal',
    SUBDOLAK: 'Subdolak'
}


### Mine class, which contains the internal state a resource node mine.
class Mine:
    def __init__(self, type, const):
        """
        Initialize a new mine. Requires the type of mine and how many extra construction (const) yards are needed to reach it.
        """
        self.type = type
        self.const = const
        self.upgrades = np.array([0, 0, 0, 0, 0, 0, 0]) # How many times the mine has been upgraded with each of the seven resource types.

        self.base_income = np.array([0, 0, 0, 0, 0, 0, 0], dtype=np.float64) 
        if self.type in {FOOD, METAL, OIL, CRYSTAL, SUBDOLAK}: # Most mines have a base income of +1 resource/round.
            self.base_income[type] = 1
        elif self.type == MANA: # Mana start at +5 mana/round.
            self.base_income[type] = 5
        elif self.type == GOLD: # Gold start at +6 mana/round.
            self.base_income[type] = 6

        self.income = self.base_income.copy() # Initialize with the mine's total income being its base income since it has no upgrades yet.

    def __str__(self):
        return f"+{self.income[self.type]} {resource_names[self.type]} mine with {self.upgrades} upgrades"

    # Functions related to upgrading a mine.
    def upgrade_cost(self, upgrade_resource):
        """
        Returns a numpy array of the cost of the specified upgrade. If the mine is maximally upgraded already, function returns False.
        Each mine can be upgraded with gold 4 to 5 times, to provide +1 more resource, and then once with each secondary resource, to provide 20% more income. 
        """
        upgrade_level = self.upgrades[upgrade_resource]
        if (upgrade_resource == GOLD): # We're trying to upgrade with gold
            if self.type != MANA: # Mine isn't a mana, which has a different gold upgrade track. 4 upgrade levels possible.
                if upgrade_level == 0:
                    return np.array([10, 0, 0, 0, 0, 0, 0], dtype=np.float64) # Costs 10 gold for first upgrade. 
                elif upgrade_level == 1:
                    return np.array([16, 0, 0, 0, 0, 0, 0], dtype=np.float64) # Costs 16 gold for second upgrade, etc..
                elif upgrade_level == 2:
                    return np.array([23, 0, 0, 0, 0, 0, 0], dtype=np.float64)
                elif upgrade_level == 3:
                    return np.array([31, 0, 0, 0, 0, 0, 0], dtype=np.float64)
                else:
                    return False # Return False is its maximally upgraded.
            else: # Mine is a mana so implement different upgrade track (it starts cheaper and can be upgraded 1 more time).
                if upgrade_level == 0:
                    return np.array([6, 0, 0, 0, 0, 0, 0], dtype=np.float64)
                elif upgrade_level == 1:
                    return np.array([10, 0, 0, 0, 0, 0, 0], dtype=np.float64)
                elif upgrade_level == 2:
                    return np.array([16, 0, 0, 0, 0, 0, 0], dtype=np.float64)
                elif upgrade_level == 3:
                    return np.array([23, 0, 0, 0, 0, 0, 0], dtype=np.float64)
                elif upgrade_level == 4:
                    return np.array([31, 0, 0, 0, 0, 0, 0], dtype=np.float64)
                else:
                    return False 
        elif (upgrade_resource == FOOD or upgrade_resource == METAL): # Upgrading with food or metal. These cost 7 resources.
            if upgrade_level == 0: # If it's not upgraded yet...
                upgrade = np.zeros([7], dtype=np.float64)
                upgrade[upgrade_resource] = 7 # Return the cost.
                return upgrade
            else:
                return False
        elif (upgrade_resource == MANA): # Upgrading with mana. This cost 18 mana.
            if upgrade_level == 0:
                return np.array([0, 0, 0, 18, 0, 0, 0], dtype=np.float64) # Return the cost.
            else:
                return False
        elif (upgrade_resource in {OIL, CRYSTAL, SUBDOLAK}): # Upgrading with oil, crystal, or subdolak. These cost 5 resources. 
            if upgrade_level == 0:
                upgrade = np.zeros([7], dtype=np.float64)
                upgrade[upgrade_resource] = 5 # Return the cost.
                return upgrade
            else:
                return False


    def update_total_income(self):
        """
        Updates the total income of the mine. Should be called after any upgrade.
        """
        self.income[self.type] = np.round((self.base_income[self.type] + self.upgrades[0]) * (1 + 0.2*np.sum(self.upgrades[1:])), 1) # Logic to calculate mine's total income given its resources. Gold upgrades (self.upgrade[0]) add one base income whereas all secondary resource (self.upgrades[1:]) upgrades increase yield by 20%. Rounds to 1 decimal point to fix floating point errors (all valid upgrades permutations will always result in most 1 decimal point).


    def upgrade_mine(self, upgrade_resource):
        """ 
        Upgrades a mine with a given resource. Assumes the logic of whether or not the upgrade is possible and affordable is handled before called.
        """
        previous_income = self.income.copy() # Get a copy of the income before upgrading.
        self.upgrades[upgrade_resource] += 1 # Apply the upgrade.
        self.update_total_income() # Updates self.income with the new income with all existing upgrades.
        new_income = self.income 
        return (new_income - previous_income) # Return the change income, which is used in GameState to keep track of total income.       


    # Methods related to purchasing a mine.
    def purchase_cost(self, num_mines):
        """
        Returns the cost to purchase a new mine.
        """
        if self.type != FOOD: # Non-food mines get more expensive with each mine.
            if num_mines == 0:
                return np.array([6, 0, 0, 0, 0, 0, 0], dtype=np.float64) # First mine costs 6 gold.
            elif num_mines == 1:
                return np.array([10, 0, 0, 0, 0, 0, 0], dtype=np.float64) # First mine costs 10 gold, etc.
            elif num_mines == 2:
                return np.array([13, 0, 0, 0, 0, 0, 0], dtype=np.float64)
            elif num_mines == 3:
                return np.array([16, 0, 0, 0, 0, 0, 0], dtype=np.float64)
            elif num_mines == 4:
                return np.array([23, 0, 0, 0, 0, 0, 0], dtype=np.float64)
            elif num_mines == 5:
                return np.array([26, 0, 0, 0, 0, 0, 0], dtype=np.float64)
            else:
                return np.array([31, 0, 0, 0, 0, 0, 0], dtype=np.float64)
        else: # Foods always cost 10.
            return np.array([10, 0, 0, 0, 0, 0, 0], dtype=np.float64)


# Normally in Mines and Magic the distribution of mines is random each game. However here we define a list representing a static distribution of mines for testing/training. Down the road maybe generate random mines. Needs to be sorted by number of required construction yards.
map_mines = [
    Mine(GOLD, 1),
    Mine(FOOD, 1),   
    Mine(METAL, 1),
    Mine(MANA, 1),
    Mine(OIL, 1),
    Mine(CRYSTAL, 1),
    Mine(SUBDOLAK, 1),
    Mine(GOLD, 2),
    Mine(FOOD, 2),   
    Mine(METAL, 2),
    Mine(MANA, 2),
    Mine(OIL, 2),
    Mine(CRYSTAL, 2),
    Mine(SUBDOLAK, 2),
    Mine(GOLD, 3),
    Mine(FOOD, 3),   
    Mine(METAL, 3),
    Mine(MANA, 3),
    Mine(OIL, 3),
    Mine(CRYSTAL, 3),
    Mine(SUBDOLAK, 3),
    Mine(GOLD, 4),
    Mine(FOOD, 4),   
    Mine(METAL, 4),
    Mine(MANA, 4),
    Mine(OIL, 4),
    Mine(CRYSTAL, 4),
    Mine(SUBDOLAK, 4), 
    Mine(GOLD, 5),
    Mine(FOOD, 5),   
    Mine(METAL, 5),
    Mine(MANA, 5),
    Mine(OIL, 5),
    Mine(CRYSTAL, 5),
    Mine(SUBDOLAK, 5),         
]


### Send class, which contains the internal state a send.
class Send:
    def __init__(self, name = '', cost = [0, 0, 0, 0, 0, 0, 0], income = 0, round = 1):
        """
        Initialize a new second.
        Needs the name of the send, the cost, how much gold income it provides, and what round it becomes available.
        """
        self.cost = np.array(cost, dtype=np.float64)
        self.income = np.array([income, 0, 0, 0, 0, 0, 0], dtype=np.float64)
        self.name = name
        self.round = round


    def __str__(self):
        return f"{self.name} Send with cost {self.cost}: total income +{self.income[0]} Gold"


    def purchase_cost(self):
        return self.cost    
    

    def get_income(self):
        return self.income
    

# List of possible sends. Needs to be sorted by round available.
sends = [
    Send('Fat Ling', [0, 3, 0, 0, 0, 0, 0], 0.7, 1),
    Send('Acid Ling', [0, 0, 3, 0, 0, 0, 0], 0.6, 1),
    Send('Drone Ling', [0, 0, 0, 9, 0, 0, 0], 0.7, 1),
    Send('Zealot', [0, 9, 0, 0, 0, 0, 0], 2.5, 5),
    Send('Marine', [0, 0, 9, 0, 0, 0, 0], 2.2, 5),
    Send('Slime', [0, 0, 0, 26, 0, 0, 0], 2.2, 5),
    Send('Mechanical Ling', [0, 0, 0, 0, 5, 0, 0], 1.5, 6), # ?
    Send('Pink Crystaling', [0, 0, 0, 0, 0, 6, 0], 1.5, 6), # ?
    Send('Scorpion', [0, 0, 0, 0, 0, 0, 5], 1.5, 6), # ?
    Send('Laserbot', [0, 0, 0, 0, 7, 7, 0], 4.4, 7), # ?
    Send('Hellion', [0, 0, 0, 0, 7, 0, 7], 4.4, 7), # ?
    Send('Pink Crystalisk', [0, 0, 0, 0, 0, 7, 7], 3.8, 7), # ?
    Send('Roach', [0, 18, 0, 0, 0, 0, 0], 4.8, 10),
    Send('Dark Reaper', [0, 0, 18, 0, 0, 0, 0], 5.5, 10),
    Send('Queen', [0, 0, 0, 50, 0, 0, 0], 5.5, 10),
    Send('Lurker', [0, 25, 0, 12, 0, 0, 0], 7, 17),
    Send('Mutalisk', [0, 0, 25, 12, 0, 0, 0], 7, 17),
    Send('Mule', [0, 0, 0, 10, 20, 0, 0], 7, 17),
    Send('Diamonster', [0, 0, 0, 10, 0, 20, 0], 7, 17),
    Send('Voidray', [0, 0, 0, 20, 0, 0, 20], 7, 17)
]


### GameState class, which keeps tracks of bank, income, round, constructed construction yards, and lists of owned and unowned mines. Provides various methods for progressing the game/performing different actions.
class GameState:

    def __init__(self, map_mines):
        """
        Instantiates a new GameState. Requires a list of Mine objects which represent the map.
        """
        self.bank = np.array([60, 0, 0, 0, 0, 0, 0], dtype=np.float64) # Start with 60 gold.
        self.income = np.array([16, 0, 0, 0, 0, 0, 0], dtype=np.float64) # Start with +16 gold income.
        self.round = 1 # Start on round 1.
        self.const = 1 # Start with 1 construction yard.
        self.owned_mines = [] # Start with no owned mines.
        self.num_mines = 0 # Start with no owned mines. 
        self.unowned_mines = copy.deepcopy(map_mines) # Populate the unowned_mines with the map.
        self.available_moves = [] # Make an empty list which contains the valid moves.
        self.update_available_actions() # Update the available moves based on the initialized game state.
        self.moves_performed = [] # Make an empty list of what moves have been performed.


    def __str__(self):
        return f"Round {self.round}: Bank: {self.bank}, Income +{self.income}, {self.const} yard(s)"
    

    ### General
    def next_round(self):
        """
        Moves onto the next round.
        """
        self.bank += self.income # Add income to the bank.
        self.round += 1 # Increases the round counter by 1.
        return "--> Next round"


    def affordable(self, cost):
        """
        Checks if something is affordable.
        """
        result = self.bank - cost # What bank would be after buying whatever it is.
        return np.all(result >= 0) # Returns True if no resource becomes negative, otherwise returns False.


    ### Mines
    def get_available_mines(self):
        """
        Iterate over unowned mines and see which are purchasable right now.
        Assumes the unowned mines are sorted by needed construction yards (for performance reasons).
        """
        available_mines = []
        for mine in self.unowned_mines: 
            if mine.const > self.const: # If don't have enough construction yards, break. Assumes self.unowned_mines is sorted by required construction yards.
                break
            if self.affordable(mine.purchase_cost(self.num_mines)): # If we can afford the mine
                available_mines.append((self.purchase_mine, (mine,))) # Add the purchase_mine method and a tuple of the required args to a list.
        return available_mines


    def purchase_mine(self, mine):
        """
        Purchase an unowned mine. 
        Subtracts cost from bank, adds to income, and moves from unowned mines to owned mines.
        """
        self.bank -= mine.purchase_cost(self.num_mines) # Subtract the cost from the bank.
        self.income += mine.income # Add the mine's income to our total income.
        if mine.type != FOOD: # If it's not a food, increase the number of mines by 1; food mines don't count towards the total.
            self.num_mines += 1
        self.owned_mines.append(mine) # Add it to list of owned mines.
        self.unowned_mines.remove(mine) # Remove it from the unowned mines.
        return f"--> Purchased {mine}" 


    def get_upgradable_mines(self):
        """
        Iterate over owned mines and see what upgrades are purchasable right now (in terms of having enough resources).
        """
        upgradable_mines = []
        for mine in self.owned_mines:  
            for resource in range(7): # Iterate over each resource.
                cost = mine.upgrade_cost(resource) # See how much it costs to upgrade with this resource.
                if isinstance(cost, np.ndarray): # If we returned a valid cost array - if it's not upgradable anymore with thie resource upgrade_cost returns False.
                    if self.affordable(cost): # If we can afford the upgrade 
                        upgradable_mines.append((self.upgrade_mine, (mine, resource))) # Add the upgrade_mine method and a tuple of the required args to a list.
        return upgradable_mines


    def upgrade_mine(self, mine, resource):
        """
        Upgrade an owned mine.
        Subtracts cost from bank, updates its internal state, and adds the difference from the previous income to income.
        """
        self.bank -= mine.upgrade_cost(resource) # Subtract the cost from the bank.
        income_delta = mine.upgrade_mine(resource) # Upgrade the internal mine state and get how much the mine's income increased by.
        self.income += income_delta # Add the delta of the mine's income to our total income.
        return f"--> Upgraded {mine}"


    ### Sends
    def purchase_send(self, send):
        """
        Purchases a given send.
        """
        self.bank -= send.cost # Subtract the cost from the bank.
        self.income += send.income # Add the send's income to our total income.
        return f"--> Purchased {send}"  


    def get_available_sends(self):
        """
        Iterate over the send options and see what sends are purchasable right now (in terms of having enough resources and it being unlocked by being current round)
        TO DO: Keep track of sends, Mines and Magic caps how many you can send per turn.
        """
        available_sends = []
        for send in sends: # "sends" is never modified and defined globally.
            if send.round > self.round: # If it's too early to access this send, break. Assumes sends is sorted by required round.
                break
            if self.affordable(send.purchase_cost()): # If we can afford the send.
                available_sends.append((self.purchase_send, (send,))) # Add the purchase_send method and a tuple of the required args to a list.
        return available_sends
    

    ### Construction Yards
    def purchase_const(self):
        """
        Adds a new construction yard, required for building on further way mines.
        """
        self.bank -= self.const_cost() # Subtract the cost from the bank.
        self.const += 1 # Increase the number of yards by 1.
        return "--> Purchased construction yard"
        

    def const_cost(self):
        """
        Returns the cost of a new construction yards. They start at 31 gold and cost goes up by 10 gold/yard.
        """
        return np.array([31 + self.const*10, 0, 0, 0, 0, 0, 0])
    

    ### Game simulation
    def update_available_actions(self):
        """
        Updates self.available_moves with a list of all the possible valid moves.
        """
        self.available_moves = []
        # Buy non-owned mines
        self.available_moves.extend(self.get_available_mines())
        # Upgrade owned mines
        self.available_moves.extend(self.get_upgradable_mines())
        # Sends
        self.available_moves.extend(self.get_available_sends())
        # Construction yard
        if (self.affordable(self.const_cost())):
            self.available_moves.append((self.purchase_const, ()))
        # Move to next round
        self.available_moves.append((self.next_round, ()))
    
    
    def show_available_actions(self, delimiter = '\n'):
        """
        Human interface to the game. Prints the available actions/moves.
        """
        action_string = ""
        for i, action in enumerate(self.available_moves):
            if i == len(self.available_moves)-1:
                delimiter = '' # After adding the last move don't add another new delimiter.
            if action[0] == self.purchase_mine:
                action_string += f"{i}: Purchase {str(action[1][0])}{delimiter}"
            elif action[0] == self.upgrade_mine:
                action_string += f"{i}: Upgrade with {resource_names[action[1][1]]}, {str(action[1][0])}{delimiter}"
            elif action[0] == self.purchase_send:
                action_string += f"{i}: Purchase {str(action[1][0])}{delimiter}"
            elif action[0] == self.purchase_const:
                action_string += f'{i}: Purchase construction yard{delimiter}'
            elif action[0] == self.next_round:
                action_string += f"{i}: Move to next round{delimiter}"

        print(action_string)


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
                max_move = len(self.available_moves)
                if 0 <= user_input < max_move: # See if it's in the range of valid moves.
                    return user_input # If it is, return it.
                else: # Not a valid move, try again.
                    print(f"Please enter a valid move between 0 and {max_move}.")
            except ValueError: # Not an int, try again.
                print(f"Please enter a valid move between 0 and {max_move}.")


    def perform_action(self, action_num):
        """
        Performs a valid move from self.available_moves.
        """
        func, args = self.available_moves[action_num] # Figure out which method to call with which arguments.
        result = func(*args) if args else func() # If the method has args pass them, otherwise just call the method.
        self.moves_performed.append(result) # Log the move.
        return result


    def play_match(self):
        """
        Implements a human interface to play a full game. Keeps looping until end of round 37 or player types exit.
        """
        print(str(self)) # Print initial bank/income/etc.
        while self.round < 38: # Keep playing until we reach end of round 37.
            self.show_available_actions() # Print the available moves.
            action = self.input_action() # Ask for an action.
            confirmation = self.perform_action(action) # Perform the action.
            print(confirmation) # Print the action
            print(str(self)) # After the action print the new bank/income/etc.
            self.update_available_actions() # Update available moves.
        print(f"---> Game complete! Finished game with bank: {self.bank}, income: {self.income}!") # Print the final bank/income.


def main():
    while True: # Keep playing games until player exists.
        print("Starting new game!") 
        gs = GameState(map_mines) # Initialize a new GameState.
        gs.play_match() # Play the game.

        play_again = input("Do you want to play again? (y/n): ") 
        if play_again.lower() != 'y': # If they don't want to play anymore
            print("Thanks for playing!")
            break # Exit.


if __name__ == "__main__":
    sys.exit(main())
