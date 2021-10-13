# ![alt text](https://kcddelizabethemsley.files.wordpress.com/2018/01/untitled-3.gif?w=40 "Dice!") Yatzy AI: A Deep Neural Network

## About
* This program trains a neural network to play the game of [Yatzy][1].
* It plays by the Scandinavian rules, where the max score is 374, and the statisically optimal strategy gives an average score of [248.68][2]
* Average score of the AI is 145 after 1000 games. More training is needed.
* It is written in Python using the [Keras][3] interface to [Tensorflow][4].

[1]: https://en.wikipedia.org/wiki/Yatzy
[2]: https://www.csc.kth.se/utbildning/kth/kurser/DD143X/dkand12/Group89Michael/report/Larsson+Sjoberg.pdf
[3]: https://keras.io/
[4]: https://www.tensorflow.org/

## Setup
* Install python dependencies `keras`, `tensorflow` and `scikit-learn`.
* If your GPU supports CUDA, you can use [Anaconda][5] to run the program with your GPU. See a tutorial [here][6].

[5]: https://www.anaconda.com/products/individual#Downloads
[6]: https://medium.com/@martin.berger/how-to-setup-gpu-accelerated-tensorflow-keras-on-windows-10-with-anaconda-3-bf844a720aa3

## Implementation
The game of Yatzy is defined in yatzy.py. A game is instantiated with a list of players (player.py), and each player is instantiated with a `Strategy` (strategy.py). The strategy defines how the player plays the game when it is that players turn to roll the die. The strategy can be set to one of the following:
* `random`: the player makes desicions based on a random generator.
* `model`: the player makes desicions based the neural networks defined in `models.py`
* `statistical`: [not yet implemented] the player makes desicions based on the statistically optimal strategy
* `human`: [not yet implemented] the player makes desicions based on input from the user.

Actions that the models take and results that these actions give needs to be saved somewhere so that we can feed it to the model later for training. This data is saved in an object of type `History` (history.py). `TrainingGame` is inherited from `Yatzy`, and its purpose is to be an environment in which to train the models. It defines its own play() function which works exactly like `Yatzy:play()` but includes writing data to its history log while the game is played, and it trains the models with that data before returning.

## UML
