import random

from core.errors import MajorError


class GameState:
    def reset(self):
        self.PlayerList = []

        self.CommonActions = [action.Income, action.ForeignAid, action.Coup]
        self.CardsAvailable = [
            action.Duke,
            action.Captain,
            action.Assassin,
            action.Ambassador,
            action.Contessa,
        ]
        self.Deck = self.CardsAvailable * 3
        random.shuffle(self.Deck)
        self.Treasury = 50
        self.RevealedCards = []

        self.randomShuffle = random.shuffle
        self.randomSelector = random.choice

    def AddToDeck(self, card):
        self.Deck.append(card)
        self.randomShuffle(self.Deck)

    def requestCallForBluffs(self, activePlayer, action, targetPlayer):
        ActiveIndex = self.PlayerList.index(activePlayer)
        PlayerList = self.PlayerList[ActiveIndex:] + self.PlayerList[0:ActiveIndex]

        if targetPlayer != None:
            TargetIndex = self.PlayerList.index(targetPlayer)
            PlayerList.remove(targetPlayer)
            PlayerList = [self.PlayerList[TargetIndex]] + PlayerList

        for player in PlayerList:
            if player == activePlayer or not player.alive:
                continue
            if player.confirmCall(activePlayer, action):
                return player
        return None

    def DrawCard(self):
        if not len(self.Deck):
            raise MajorError("There is no card in the court deck!")

        card = self.randomSelector(self.Deck)
        self.Deck.remove(card)
        return card

    def getBlockingActions(self, action):
        """
        returns all the cards the block an action
        """
        blockers = []
        for card in GameState.CardsAvailable:
            if action.name in card.blocks:
                blockers.append(card)

        return blockers

    def requestBlocks(self, activePlayer, action, targetPlayer):
        ActiveIndex = self.PlayerList.index(activePlayer)
        PlayerList = self.PlayerList[ActiveIndex:] + self.PlayerList[0:ActiveIndex]

        if targetPlayer != None:
            TargetIndex = self.PlayerList.index(targetPlayer)
            PlayerList.remove(targetPlayer)
            PlayerList = [self.PlayerList[TargetIndex]] + PlayerList

        for player in PlayerList:
            if player == activePlayer or not player.alive:
                continue

            blockingAction = player.confirmBlock(activePlayer, action)

            if blockingAction != None:
                # check that the block is valid
                if not action.name in blockingAction.blocks:
                    continue

                return player, blockingAction

        return None, None


GameState = GameState()

from . import action
