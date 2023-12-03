import random
from core.action import Coup, ForceCoupCoins
from core.errors import ActionNotAllowed, DeadPlayer, NotEnoughCoins, TargetRequired
from core.game import GameState


class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self.name = "No name"
        self.displayName = ""

        self.human = False
        self.coins = 2
        self.alive = True

        card1 = GameState.DrawCard()
        card2 = GameState.DrawCard()
        self.influence = [card1, card2]

        GameState.PlayerList.append(self)

    def play(self, action, target=None):
        if not self.alive or (target != None and not target.alive):
            raise DeadPlayer

        if target == self:
            raise TargetRequired

        if self.coins < action.coinsNeeded:
            raise NotEnoughCoins(action.coinsNeeded)

        if self.coins >= ForceCoupCoins and action != Coup:
            raise ActionNotAllowed(
                "Player has %i coins. Forced Coup is the only allowed action"
                % (self.coins)
            )

        # calling for bluff
        callingPlayer = None
        if action in GameState.CardsAvailable:
            callingPlayer = GameState.requestCallForBluffs(self, action, target)

        if callingPlayer != None:
            if action in self.influence:
                # active player is telling the truth. Return the card back to the deck.
                index = self.influence.index(action)
                card = self.influence[index]
                self.influence.remove(card)
                GameState.AddToDeck(card)
                card = GameState.DrawCard()
                self.influence.append(card)

                callingPlayer.loseInfluence()
            else:
                self.loseInfluence()
                message = "Bluffing %s failed for %s" % (
                    action.displayName,
                    self.displayName,
                )
                return False, message

        # blocking
        blockingPlayer = None

        if len(GameState.getBlockingActions(action)):
            blockingPlayer, blockingAction = GameState.requestBlocks(
                self, action, target
            )

        if blockingPlayer != None:
            if self.confirmCall(blockingPlayer, blockingAction):
                if blockingAction in blockingPlayer.influence:
                    self.loseInfluence()
                    message = "Player %s has %s. Player %s loses influence." % (
                        blockingPlayer.displayName,
                        blockingAction.displayName,
                        self.displayName,
                    )
                    blockingPlayer.changeCard(blockingAction)
                    return False, message
                else:
                    blockingPlayer.loseInfluence()
            else:
                message = "Blocked by %s" % blockingPlayer.displayName
                return False, message

        # Step 5
        status, response = action.play(action, self, target)
        return status, response

    def confirmCall(self, activePlayer, action):
        """return True if player confirms call for bluff on active player's action. returns False if player allows action."""
        return False

    def confirmBlock(self, activePlayer, opponentAction):
        """returns action used by player to blocks action. return None if player allows action."""
        return None

    def loseInfluence(self):
        loses = self.selectInfluenceToDie()

        if loses != None:
            self.influence.remove(loses)
        if len(self.influence) == 0:
            self.alive = False
            self.name = self.name
        GameState.RevealedCards.append(loses)

    def selectInfluenceToDie(self):
        """select an influence to die. returns the value from the influence list."""

        return random.choice(self.influence)

    def selectAmbassadorInfluence(self, choices, influenceRemaining):
        """returns one or two cards from the choices."""
        selected = []

        for i in range(influenceRemaining):
            card = random.choice(choices)
            selected.append(card)
            choices.remove(card)
        return selected

    def changeCard(self, card):
        if not card in self.influence:
            raise BaseException(
                "%s is not found in player's influence. Something went wrong" % card
            )

        self.influence.remove(card)
        GameState.AddToDeck(card)

        newCard = GameState.DrawCard()
        self.influence.append(newCard)
