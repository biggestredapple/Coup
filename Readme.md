# How to run application

```
python version > 3.x
```

run application: `python main.py`

# Requirement

Coup is a simple party card game with basic rules.
https://www.ultraboardgames.com/coup/game-rules.php
For this project, you will be writing your version of the game in Python.
After you finish the project, you can use it as a part of your public portfolio! You own the source code that you create

UI:

1. The design of the UI can be very simple and minimalistic or even non-existent, you will not be judged on the visual appeal of your design.
   No images will be needed, you can use colored squares, HTML divs, or even write the whole game in command-line.
2. You may freely choose libraries as you desire (e.g. Flask, Bootstrap, PIL)
3. Feel free to be creative about simplifying the board to make the interactions simple. You won't be judged on the quality of your interaction design.
4. For the cards, please represent each card with the following colors: contessa red, duke purple, captain blue, ambassador green, assassin black (if using command-line, use command-line colors)
5. Coins should be gray
6. For clarity, each action which is taken in the game should be 'announced' in a text display e.g. "Player 1 chose to Blocked Foreign Aid for Player 2"
7. Bonus points will be given if you can write a super simple Flask server that renders the game in an HTML page. But this is totally not required, command line is really okay

Game Logic:

1. Each of the game phases of Coup should be represented in the code
2. The player should be able to restart the game after the game ends
3. Structurally there should be a clear separation of View and Controller (Ul logic from game logic)
4. Player1 will be a human, the other players will be Al
5. The Al will make decisions randomly from the choices that are available to them (no intelligence needed for the AI)
6. The Al should take 1 second to make their random decision
7. Architecturally, the decisions offered to the human player should be similar to the decisions offered to the Al
8. You don't need to implement every skill for every class, focus on the ones which you think are the most interesting.
   Implement as many as you feel is feasible within the time you have
   What will we be judging?
9. We will be looking for clarity, simplicity, and elegance in the structure of the game architecture.
   The game is simple but there are more or less elegant ways to implement the game.
   We're not looking for a highly scalable, efficient, or extensible implementation
   (for example we don't need pooling and we don't need an abstract card skill class that can be extended to do literally anything).
   The ideal implementation will be no more complex than necessary and will have organized the game logic in a natural way.
   e.g. the logic of the core game does not not treat player and Al in different ways outside of decision making and UI.
10. We will be reading the code for style and other indicators of code quality.
    We understand that this is a short project so we don't expect perfect code. Efficiency of code execution is not very important

```

```
