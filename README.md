# ![alt text](https://kcddelizabethemsley.files.wordpress.com/2018/01/untitled-3.gif?w=40 "Dice!") Yatzy AI: A Deep Neural Network

## About
* This program trains a neural network to play the game of [Yatzy][1].
* It plays by the Scandinavian rules, where the max score is 374, and the statisically optimal strategy gives an average score of [248.68][2]
* Average score of the AI is yet unknown. More training is needed.
* It is written in Python using the [Keras][3] interface to [Tensorflow][4].

[1]: https://en.wikipedia.org/wiki/Yatzy
[2]: https://www.csc.kth.se/utbildning/kth/kurser/DD143X/dkand12/Group89Michael/report/Larsson+Sjoberg.pdf
[3]: https://keras.io/
[4]: https://www.tensorflow.org/

## Setup
* install python dependencies
   * `pip3 install keras tensorflow scikit-learn`
* set `LongPathsEnabled` to 1 in "registry editor" path: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem` (Windows)
* If your GPU supports CUDA, you can use [Anaconda][5] to run the program with your GPU. See a tutorial [here][6].

[5]: https://www.anaconda.com/products/individual#Downloads
[6]: https://medium.com/@martin.berger/how-to-setup-gpu-accelerated-tensorflow-keras-on-windows-10-with-anaconda-3-bf844a720aa3