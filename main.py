import os
import random
import time
import core.action as action
from core.game import GameState
from core.player import Player


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


defaultNames = ["Leonardo", "Michelangelo", "Raphael", "Donatello", "Splinter", "April"]

Players = []
PlayersAlive = []

AvailableActions = []

CurrentPlayer = 0
HumanCount = 1
GameIsRunning = True


class CardPlayer(Player):
    ShowBlockOptions = True

    def confirmCall(self, activePlayer, action):
        """return True if player confirms call for bluff on active player's action. returns False if player allows action."""
        if len(PlayersAlive) > 2:
            longestName = [len(player.name) for player in PlayersAlive]
            longestName = max(longestName)
            name = self.displayName + "," + (" " * (longestName - len(self.name)))
        else:
            name = self.displayName + ","

        choice = ""
        if not self.human:
            print(
                "%s do you think %s's %s is a bluff?\n Do you want to call (Y/N)? "
                % (name, activePlayer.displayName, action.displayName),
                end="",
            )
            choice = random.choice(["Y", "N"])
            time.sleep(1.5)
            print(choice)
        else:
            choice = input(
                "%s do you think %s's %s is a bluff?\n Do you want to call (Y/N)? "
                % (name, activePlayer.displayName, action.displayName)
            )
            choice = choice.upper()

        if not choice.strip() in ("Y", "N", ""):
            print(
                "\n Type Y to call bluff. \n Type N or press enter to allow %s's %s.\n"
                % (activePlayer.displayName, action.displayName)
            )
            return self.confirmCall(activePlayer, action)

        if choice == "Y":
            return True

        return False

    def selectInfluenceToDie(self):
        """select an influence to die. returns the value from the influence list."""
        if len(self.influence) < 1:
            return None

        print("\n%s has lost an influence!" % (self.displayName))

        if len(self.influence) == 1:
            print(
                "%s will lose their last card, %s"
                % (self.displayName, self.influence[0].displayName)
            )
            return self.influence[0]

        print("%s, select influence to lose:" % (self.displayName), end="")
        choice = None
        if not self.human:
            time.sleep(1.5)
            choice = random.choice(self.influence)
            print(" %s" % (choice.displayName))
            return choice
        if self.human == True:
            print("\n")
            for i, card in enumerate(self.influence):
                print(" %i: %s" % (i + 1, card.displayName))
            choice = input("> ")
            if not choice.isnumeric():
                print("Invalid choice, try again\n")
                return self.selectInfluenceToDie()
            choice = int(choice)
            if not (choice == 1 or choice == 2):
                print("Invalid choice, try again\n")
                return self.selectInfluenceToDie()
            if choice > len(self.influence):
                print("Invalid choice, try again\n")
                return self.selectInfluenceToDie()

            return self.influence[choice - 1]

    def confirmBlock(self, activePlayer, opponentAction):
        """returns action used by player to blocks action. return None if player allows action."""
        cardBlockers = []

        for card in GameState.CardsAvailable:
            if opponentAction.name in card.blocks:
                cardBlockers.append(card)

        totalBlockers = len(cardBlockers) + 1

        if CardPlayer.ShowBlockOptions:
            CardPlayer.ShowBlockOptions = False

            print(
                "\n%s's %s can be blocked with the following cards:"
                % (activePlayer.displayName, opponentAction.displayName)
            )
            for i, card in enumerate(cardBlockers):
                print(" %i: %s" % (i + 1, card.displayName))
            print(" %i: (Do not block)\n" % (totalBlockers))

        if len(PlayersAlive) > 2:
            longestName = [len(player.name) for player in PlayersAlive]
            longestName = max(longestName)
            name = self.displayName + "," + (" " * (longestName - len(self.name)))
        else:
            name = self.displayName + ","

        choice = None
        if not self.human:
            print(
                "%s do you wish to block %s (1-%i)? "
                % (name, opponentAction.displayName, totalBlockers),
                end="  ",
            )
            choice = random.randint(0, len(cardBlockers))
            time.sleep(1.5)

            if choice >= 0 and choice < len(cardBlockers):
                print(cardBlockers[choice].displayName)
                print(
                    "\n\n%s is blocking with %s"
                    % (self.displayName, cardBlockers[choice].displayName)
                )
                return cardBlockers[choice]
            else:
                print("(Do not block)")
                return None

        choice = input(
            "%s do you wish to block %s (1-%i)? "
            % (name, opponentAction.displayName, totalBlockers)
        )
        choice = choice.strip()
        if choice == "":
            choice = str(totalBlockers)  # do not block

        if not choice.isnumeric():
            print(
                " Select a number between 1-%i. Press enter to allow %s's %s."
                % (totalBlockers, activePlayer.displayName, opponentAction.displayName)
            )
            return self.confirmBlock(activePlayer, opponentAction)
        choice = int(choice) - 1

        if choice == len(cardBlockers):
            return None  # player decides not to block

        if not (choice >= 0 and choice < len(cardBlockers)):
            print(
                " Select a number between 1-%i. Press enter to allow %s's %s."
                % (totalBlockers, activePlayer.displayName, opponentAction.displayName)
            )
            return self.confirmBlock(activePlayer, opponentAction)

        block = cardBlockers[choice - 1]

        print("\n\n%s is blocking with %s" % (self.displayName, block.displayName))
        return block

    def selectAmbassadorInfluence(self, choices, influenceRemaining):
        """returns one or two cards from the choices."""
        finalChoices = []

        def askChoice(choices, inputMessage):
            print("")
            for i, choice in enumerate(choices):
                if self.human:
                    print(" %i: %s" % (i + 1, choice.displayName))
                    print("")

            if not self.human:
                card = random.choice(choices)
                return card

            card = input(inputMessage)

            if not card.isnumeric():
                return askChoice(choices, inputMessage)

            card = int(card) - 1
            if card < 0 or card >= len(choices):
                return askChoice(choices, inputMessage)

            card = choices[card]
            return card

        ClearScreen("Ambassador success", 24)

        if self.human:
            print("\n%s, these are the cards you drew:" % (self.displayName))

        card1 = askChoice(choices, "Select the first card to take> ")
        choices.remove(card1)

        if influenceRemaining == 1:
            if not self.human:
                time.sleep(1.5)
                print(
                    "%s successfully exchanged cards with the Court"
                    % (card1.displayName)
                )
            return [card1]
        else:
            print("")
            card2 = askChoice(choices, "Select the second card to take>")
            if not self.human:
                time.sleep(1.5)
                print(
                    "%s successfully exchanged cards with the Court"
                    % (card2.displayName)
                )
            return [card1, card2]


def ClearScreen(headerMessage, headerSize=10):
    os.system("cls" if os.name == "nt" else "clear")

    dic = {
        "\\": b"\xe2\x95\x9a",
        "-": b"\xe2\x95\x90",
        "/": b"\xe2\x95\x9d",
        "|": b"\xe2\x95\x91",
        "+": b"\xe2\x95\x94",
        "%": b"\xe2\x95\x97",
    }

    def decode(x):
        return "".join(dic.get(i, i.encode("utf-8")).decode("utf-8") for i in x)

    print(Colors.BLUE + decode("+%s%%" % ("-" * headerSize)))
    print(Colors.BLUE + decode("|%s|" % (headerMessage.center(headerSize))))
    print(Colors.BLUE + decode("\\%s/" % ("-" * headerSize)) + Colors.RESET)


def SetupActions():
    global AvailableActions
    for action in GameState.CommonActions:
        AvailableActions.append(action)
    for action in GameState.CardsAvailable:
        AvailableActions.append(action)


def Setup():
    # Generate the player list
    # Shuffle the player list
    GameState.reset()
    SetupActions()

    def GetNumberOfPlayers():
        PlayerCount = input(Colors.RESET + "How many players (2-6)? ")
        if not PlayerCount.isnumeric():
            return GetNumberOfPlayers()

        PlayerCount = int(PlayerCount)
        if PlayerCount < 2 or PlayerCount > 6:
            return GetNumberOfPlayers()
        return PlayerCount

    PlayerCount = GetNumberOfPlayers()

    def CreatePlayer(Number, Human=False):
        player = CardPlayer()

        player.name = ""
        player.displayName = ""
        if Human == True:
            player.name = input(
                Colors.RESET
                + "Player #%i: What is your name (Leave blank for a random name)? "
                % (Number + 1)
                + Colors.CYAN
                + ""
            )
            player.displayName = Colors.CYAN + player.name + Colors.RESET

            if player.name.strip() == "":
                player.name = random.choice(defaultNames)
                player.displayName = Colors.CYAN + player.name + Colors.RESET
                defaultNames.remove(player.name)
                print(
                    Colors.RESET
                    + " Player"
                    + Colors.CYAN
                    + " %i" % (Number + 1)
                    + Colors.RESET
                    + "'s name is"
                    + Colors.CYAN
                    + " %s\n" % (player.name)
                    + Colors.RESET
                )

            player.human = True
        else:
            player.name = "Computer %i " % (Number + 1)
            player.displayName = Colors.CYAN + player.name + Colors.RESET

        return player

    print("\n")

    for i in range(PlayerCount):
        global HumanCount
        Players.append(CreatePlayer(i, HumanCount > 0))
        HumanCount -= 1

    input(Colors.RESET + "\n press ENTER to continue")
    random.shuffle(Players)

    global PlayersAlive
    PlayersAlive = [player for player in Players if player.alive]


def PrintTurnOrder(currentPlayerShown):
    header = [" Turn Order", ""]

    for i, player in enumerate(Players):
        headerStr = "   %i: %s" % (i + 1, player.name)
        if player == currentPlayerShown:
            headerStr = "  >" + headerStr.strip()
        header.append(headerStr)

    maxLen = max([len(row) for row in header]) + 2
    for i, row in enumerate(header):
        header[i] = row + (" " * (maxLen - len(row)))

    header[1] = "-" * maxLen

    ClearScreen("|\n|".join(header), maxLen)


def PrintDickList():
    print(Colors.BLACK + "There are %i cards in the Court Deck" % (len(GameState.Deck)))
    print(Colors.RESET + "\n")


def PrintRevealedCards():
    size = len(GameState.RevealedCards)
    if size == 0:
        return

    print(Colors.BLACK + "There are %i cards that has been revealed:" % (size))

    reveals = [card.displayName for card in GameState.RevealedCards]
    reveals.sort()
    for card in reveals:
        print(Colors.BLACK + "   ", card)
    print(Colors.RESET + "\n")


def PrintActions():
    for i, action in enumerate(AvailableActions):
        if action.name != "Contessa":  # ignore Contessa as a possible action.
            print(" %i: " % (i + 1) + "%s" % (action.displayName))
    print(" X:" + Colors.WHITE + " Exit the game" + Colors.RESET)


def MainLoop():
    global PlayersAlive, CurrentPlayer, GameIsRunning

    GameIsRunning = True
    while GameIsRunning and len(PlayersAlive) > 1:
        player = Players[CurrentPlayer]
        CardPlayer.ShowBlockOptions = True

        def PrintInfo():
            PlayerList = Players[CurrentPlayer:] + Players[0:CurrentPlayer]
            paddingWidth = 16
            headerList = []
            headerStr = ""
            rowWidth = 0

            for playerInfo in PlayerList:
                name = playerInfo.name
                if len(name) > paddingWidth - 4:
                    name = name[: paddingWidth - 4] + "... "
                padding = " " * (paddingWidth - len(name))
                headerStr += name + padding

            headerStr = headerStr.rstrip()
            rowWidth = max(rowWidth, len(headerStr) + 4)
            headerStr = "  " + headerStr
            headerList.append(headerStr)
            headerStr = ""

            for playerInfo in PlayerList:
                coins = playerInfo.coins
                coins = "Coins: %i" % (coins)
                coins = coins.rjust(2)

                padding = " " * (paddingWidth - len(coins))
                headerStr += coins + padding

            headerStr = "  " + headerStr
            headerStr = headerStr.rstrip()
            rowWidth = max(rowWidth, len(headerStr))
            rowWidth = max(rowWidth, len(headerStr))
            headerList.append(headerStr)

            headerStr = "(Active player)" + (paddingWidth * " ")
            rowWidth = max(rowWidth, len(headerStr))
            headerList.append(headerStr)

            for i, header in enumerate(headerList):
                headerList[i] += " " * (rowWidth - len(headerList[i]))

            ClearScreen("|\n|".join(headerList), rowWidth)

            print("")
            PrintDickList()
            PrintRevealedCards()
            if player.human:
                print("\n\n%s" % (player.displayName) + Colors.RESET + "'s cards are: ")
                heldCards = " and ".join(
                    [card.displayName for card in player.influence]
                )
                print("    " + heldCards)

        def Cleanup():
            global CurrentPlayer
            CurrentPlayer += 1
            if CurrentPlayer >= len(Players):
                CurrentPlayer = 0

            global PlayersAlive
            PlayersAlive = [player for player in Players if player.alive]

        def ChooseAction():
            move = 0
            if not player.human:
                move = random.randint(0, len(AvailableActions) - 2)
                time.sleep(1)
                print(
                    "\n%s" % (player.displayName)
                    + Colors.RESET
                    + " selected %s action" % (AvailableActions[move].displayName)
                )
            else:
                move = input("Action> ")
                if not move.isnumeric():
                    if move.upper() == "X":
                        confirm = input(
                            Colors.BLACK
                            + "\nAre you sure you want to exit (Y/N)? "
                            + Colors.RESET
                            + ""
                        )
                        if confirm.upper() != "Y":
                            ChooseAction()
                            return

                        global GameIsRunning
                        GameIsRunning = False
                        return
                    ChooseAction()
                    return
                move = int(move) - 1

                if not (move >= 0 and move < len(AvailableActions)):
                    ChooseAction()
                    return

            status = False

            def ChooseTarget():
                PossibleTargets = list(Players)
                PossibleTargets.remove(player)

                PossibleTargets = [player for player in PossibleTargets if player.alive]

                if not player.human:
                    targetIndex = random.randint(0, len(PossibleTargets) - 1)
                    time.sleep(1.5)
                    print(
                        "%s selected %s as a target"
                        % (player.displayName, PossibleTargets[targetIndex].displayName)
                    )
                    return PossibleTargets[targetIndex]

                if len(PossibleTargets) == 1:
                    return PossibleTargets[0]

                print()
                for i, iterPlayer in enumerate(PossibleTargets):
                    print(" %i: %s" % (i + 1, iterPlayer.displayName))
                target = input("Choose a target> ")

                if not target.isnumeric():
                    return ChooseTarget()
                target = int(target) - 1
                if target < 0 or target >= len(PossibleTargets):
                    return ChooseTarget()

                return PossibleTargets[target]

            if player.coins < AvailableActions[move].coinsNeeded:
                print(
                    " You need %i coins to play %s. You only have %i coins."
                    % (
                        AvailableActions[move].coinsNeeded,
                        AvailableActions[move].displayName,
                        player.coins,
                    )
                )
                ChooseAction()
                return

            if (
                player.coins >= action.ForceCoupCoins
                and AvailableActions[move].name != "Coup"
            ):
                print(
                    "Player has %i coins. Forced Coup is the only allowed action"
                    % (player.coins)
                )
                ChooseAction()
                return

            target = None
            if AvailableActions[move].hasTarget:
                target = ChooseTarget()

            if not player.human:
                input("\nPress Enter to Continue")

            try:
                header = []
                headerStr = "%s is playing %s" % (
                    player.name,
                    AvailableActions[move].name,
                )
                headerLen = len(headerStr) + 4
                headerStr = headerStr.center(headerLen)
                header.append(headerStr)

                if not target is None:
                    headerStr = " (target: %s)" % (target.name)
                    headerStr += " " * (headerLen - len(headerStr))
                    header.append(headerStr)

                ClearScreen("|\n|".join(header), headerLen)
                print("")
                status, response = player.play(AvailableActions[move], target)
            except action.ActionNotAllowed as e:
                print(e.message)
                ChooseAction()
                return
            except action.NotEnoughCoins as exc:
                print(
                    " You need %i coins to play %s. You only have %i coins."
                    % (exc.coinsNeeded, AvailableActions[move].name, player.coins)
                )
                ChooseAction()
                return
            except action.BlockOnly:
                print("You cannot play %s as an action" % (AvailableActions[move].name))
                ChooseAction()
                return
            except action.TargetRequired:
                print("You need to select a valid target.\n")
                if player.human:
                    PrintActions()
                ChooseAction()
                return

            if status == False:
                print(response)

        if player.alive:
            PrintInfo()
            if player.human == True:
                print(Colors.RESET + "\nAvailable actions:")
                PrintActions()
            ChooseAction()

        Cleanup()
        if GameIsRunning:
            input(
                "\n%s, press enter key to take next turn..."
                % Players[CurrentPlayer].displayName
            )

        if len(PlayersAlive) == 1:
            ClearScreen("The winner is %s" % (PlayersAlive[0].displayName), 79)
            input("\nPress Enter to Continue")
            for player in Players:
                player.alive = True
                card1 = GameState.DrawCard()
                card2 = GameState.DrawCard()
                player.influence = [card1, card2]
                player.coins = 2
                GameState.Deck = GameState.CardsAvailable * 3
                random.shuffle(GameState.Deck)
                GameState.RevealedCards = []

                PrintTurnOrder(player)
                if player.human == True:
                    input(
                        "\n%s " % player.displayName + ", press ENTER to see your cards"
                    )
                    padding = " " * (len(player.name) + 2)
                    heldCards = Colors.RESET + " and ".join(
                        [card.displayName for card in player.influence]
                    )
                    print("\n%s\n" % (padding + heldCards))
                    input("%sPress ENTER to hide your cards" % (padding))
                else:
                    print(
                        "\n%s has given the cards, " % (player.displayName)
                        + Colors.YELLOW
                        + "waiting..."
                        + Colors.RESET
                    )
                    time.sleep(1)
            Cleanup()


def main():
    ClearScreen("Game Setup", 50)
    print(Colors.BLACK + "Black")
    Setup()

    for player in Players:
        PrintTurnOrder(player)
        if player.human == True:
            input("\n%s " % player.displayName + ", press ENTER to see your cards")
            padding = " " * (len(player.name) + 2)
            heldCards = Colors.RESET + " and ".join(
                [card.displayName for card in player.influence]
            )
            print("\n%s\n" % (padding + heldCards))
            input("%sPress ENTER to hide your cards" % (padding))
        else:
            print(
                "\n%s has given the cards, " % (player.displayName)
                + Colors.YELLOW
                + "waiting..."
                + Colors.RESET
            )
            time.sleep(1)

    ClearScreen("Game start", 14)
    MainLoop()


if __name__ == "__main__":
    main()
