# ![alt text](https://kcddelizabethemsley.files.wordpress.com/2018/01/untitled-3.gif?w=40 "Dice!") Yatzy AI: A Deep Neural Network

## About
* This program trains a neural network to play the game of [Yatzy][1].
* It plays by the Scandinavian rules, where the max score is 374, and the statisically optimal strategy gives an average score of [248.68][2]
* Average score of the `AI` player is ??? after 100 games.
* Average score of the `Random` player is 115 with a 186 high score.
* It is written in Python using the [Keras][3] interface to [Tensorflow][4].

[1]: https://en.wikipedia.org/wiki/Yatzy
[2]: https://www.csc.kth.se/utbildning/kth/kurser/DD143X/dkand12/Group89Michael/report/Larsson+Sjoberg.pdf
[3]: https://keras.io/
[4]: https://www.tensorflow.org/

## Setup
* Install python dependencies `keras`, `tensorflow`, `scikit-learn`, `numpy`.
* If your GPU supports CUDA, you can use [Anaconda][5] to run the program with your GPU. See a tutorial [here][6].

[5]: https://www.anaconda.com/products/individual#Downloads
[6]: https://medium.com/@martin.berger/how-to-setup-gpu-accelerated-tensorflow-keras-on-windows-10-with-anaconda-3-bf844a720aa3

## Implementation
The game of Yatzy is defined in yatzy.py. A game is instantiated with a list of players. There are multiple types of player, each have their own way of playing the game when it is their turn to roll the die. These are the types players:
* `Random`: the player makes almost random desicions. It uses some rules of thumb.
* `AI`: the player makes desicions based the neural networks defined in `models.py`
* `Human`: the player makes desicions based on input from the user.
* `Statistical`: [not yet implemented] the player makes desicions based on the statistically optimal strategy

The desicions that the players make and the consequenses that these desicions have needs to be saved somewhere so that we can feed it to the models later for training. This data is saved in an object of type `History` (history.py).
