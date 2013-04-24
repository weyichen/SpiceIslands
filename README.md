Spice Islands
=============

Outline
-------
Spice Islands is a turn-based, single player exploration game in which
the player races to collect the exotic resources of an archipelago before time runs out.
Each time the game begins, a random map of scattered islands is created. A ship sprite representing
the player's vessel begins in a partly random location in the deep sea away from any specific island.

The player can navigate the ocean by clicking on the squares to which he or she desires to navigate.
The ship can only move a few squares at a time. There is a limit on the number of turns available and the
number of moves that the player can make per turn.

When the player's mouse hovers over a square on the map, that square is evaluated as a potential travel destinnation.
The square is framed in red if it is inaccessible because it is too far away from the ship or is landlocked 
(the ship cannot enter the interior of islands). If the player clicks on a red square, nothing happens.
If the destination is an accessible marine square, it is framed in yellow instead. If the player clicks on a yellow square,
the ship will move to that square and the player will lose a number of remaining available moves corresponding to the distance
traveled. Finally, if the destination is an accessible port square (on the border between an island and the ocean),
the square is framed in green. If the player clicks on a green square, the ship will move to that location. Furthermore,
if the player has visited this island for the first time, he or she will collect a randomly generated spice. If this spice
causes the player's spice collection to contain the desired set of spices, victory is achieved. If the player plays through
all available turns without collecting the necessary spices, the game is over and the player loses.

A sidebar on the left of the map displays a list of the spices collected so far, the quantity of spices collected, and the
names of the islands that the player has visited. The sidebar also reports the number of remaining moves available in this
turn, as well as the number of turns remaining in the game.

For instructions on setting up and playing Spice Islands, see please see requirements.txt.
