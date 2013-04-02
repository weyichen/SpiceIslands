CIS 192 Project Proposal
=======================

Team members: Anand Sundaram, Yichen Wei
Project Title: Spice Islands
Github Repository: https://github.com/weyichen/SpiceIslands

Outline
--------
We plan to make an exploration game. Our original game description is as follows: 

A turn-based, multiplayer strategy game in which multiple players compete to exploit the exotic resources of an archipelago within a fixed number of turns. All players start out in the same position on the map, which is a neutral zone. At first, the rest of the map is concealed by “fog of war.” Players must venture out into the high seas to explore the archipelago for resources that can be acquired and traded. Only spices can be sold for money, and the richest player wins at the end of the game, but other resources can help you collect spices more efficiently or thwart your rivals.

We have modified our specific goals to be more precise and less ambitious.

Specific goals
---------------

*Needs*
- Exploration Game
- Single Player Mode
- Random Number Generator to create unpredictable events in the game
- Randomly generate a new map with different geographical features and distribution of resources for every new game
- Character model and geographical feature graphics will be done using static sprites.
- A static map that refreshes on a turn-by-turn basis.
- Spices that the player must collect in order to win the game

*Wants*
- 2-5 players can play together sitting side-by-side and each taking turns, or have matches over the internet
- Players can battle or steal from each other in their race to collect spices
- Optional resources other than spices that give the user some indirect advantage
- In-game obstacles can be controlled by an AI
- Animated graphics for events and transitions between turns
- Use fog of war


Division of labor
----------------
Since there are only 2 group members and neither of us is specialized in any particular area of Python, we will not be designating any division of labor in the beginning, and simply learn and work on what is needed at the moment. If necessary, we will figure out an equitable distribution of labor later.

Packages
--------
pygame
flask
requests
