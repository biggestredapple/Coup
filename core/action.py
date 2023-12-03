from core.errors import *
from core.game import GameState


class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BLACK = "\033[90m"
    ORANGE = "\033[38;5;208m"
    PINK = "\033[38;5;206m"
    GOLDEN = "\033[38;5;220m"


ForceCoupCoins = 10


class Action:
    name = ""
    displayName = Colors.RESET + "" + Colors.RESET
    description = ""
    blocks = []
    hasTarget = False
    coinsNeeded = 0

    def play(self, player, target=None):
        return False, None


class Income(Action):
    name = "Income"
    displayName = Colors.WHITE + "Income" + Colors.RESET
    description = "Take 1 coin from the Treasury"

    def play(self, player, target=None):
        player.coins += 1
        return True, "Success"


class ForeignAid(Action):
    name = "Foreign Aid"
    displayName = Colors.ORANGE + "Foreign Aid" + Colors.RESET
    description = "Take 2 coins from the Treasury"

    def play(self, player, target=None):
        player.coins += 2
        return True, "Success"


class Coup(Action):
    name = "Coup"
    displayName = Colors.PINK + "Coup" + Colors.RESET
    description = "Pay 7 coins to launch a Coup against another player"
    hasTarget = True
    coinsNeeded = 7

    def play(self, player, target=None):
        if player.coins < self.coinsNeeded:
            raise NotEnoughCoins(self.coinsNeeded)

        # target should be alive
        if target == None:
            raise TargetRequired

        if not target.alive:
            raise InvalidTarget("Target is dead")

        player.coins -= 7
        target.loseInfluence()
        return True, "Success"


class Duke(Action):
    name = "Duke"
    displayName = Colors.PURPLE + "Duke" + Colors.RESET
    description = "Take 3 coins from the Treasury"
    blocks = ["Foreign Aid"]

    def play(self, player, target=None):
        player.coins += 3
        return True, "Success"


class Captain(Action):
    name = "Captain"
    displayName = Colors.BLUE + "Captain" + Colors.RESET
    description = "Steal 2 coins from another player"
    blocks = ["Captain"]
    hasTarget = True

    def play(self, player, target=None):
        if target == None:
            raise TargetRequired

        steal = 0
        if target.coins >= 2:
            steal = 2
        elif target.coins == 1:
            steal = 1

        target.coins -= steal
        if target.coins < 0:
            target.coins = 0
        player.coins += steal

        return True, "Success"


class Contessa(Action):
    name = "Contessa"
    displayName = Colors.RED + "Contessa" + Colors.RESET
    description = "Blocks Assassination."
    blocks = ["Assassin"]

    def play(self, player, target=None):
        raise BlockOnly


class Assassin(Action):
    name = "Assassin"
    displayName = Colors.BLACK + "Assassin" + Colors.RESET
    description = "Pay 3 coins to assassinate against another player."
    blocks = []
    hasTarget = True
    coinsNeeded = 3

    def play(self, player, target=None):
        if player.coins < self.coinsNeeded:
            raise NotEnoughCoins(self.coinsNeeded)
        if target == None:
            raise TargetRequired

        player.coins -= 3
        target.loseInfluence()

        return True, "Success"


class Ambassador(Action):
    name = "Ambassador"
    displayName = Colors.GREEN + "Ambassador" + Colors.RESET
    description = "Exchange cards from the Court Deck."
    blocks = ["Captain"]

    def play(self, player, target=None):
        influenceRemaining = len(player.influence)
        choices = list(player.influence)

        deckCards = [GameState.DrawCard(), GameState.DrawCard()]
        choices.append(deckCards[0])
        choices.append(deckCards[1])

        newInfluence = player.selectAmbassadorInfluence(
            list(choices), influenceRemaining
        )
        if type(newInfluence) != list:
            newInfluence = [newInfluence]

        def ReturnCards():
            GameState.AddToDeck(deckCards[0])
            GameState.AddToDeck(deckCards[1])

        if len(newInfluence) != influenceRemaining:
            # There is a missing card. Try again.
            ReturnCards()
            raise InvalidTarget("Wrong number of cards given")

        choicesCopy = list(choices)
        for card in newInfluence:
            if not card in choicesCopy:
                # something is wrong. The player sent a card choice that is not part of the original choices.
                # try again.
                ReturnCards()
                raise InvalidTarget("Card given not part of valid choices")

            choicesCopy.remove(card)

        # give the player their new cards
        player.influence = list(newInfluence)

        # return the unselected cards back to the Court Deck.
        for card in newInfluence:
            choices.remove(card)

        for card in choices:
            GameState.AddToDeck(card)
        return True, "Success"
