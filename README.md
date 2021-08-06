# Deep Learning Yatzy

## About
* This program trains a neural network to play the game of Yatzy (https://en.wikipedia.org/wiki/Yatzy).
* It plays by the scandinavian rules, where the max score is 374, and the statisically optimal strategy gives an avg. score of 248.68 (according to https://www.csc.kth.se/utbildning/kth/kurser/DD143X/dkand12/Group89Michael/report/Larsson+Sjoberg.pdf)
* Avg. score of the AI is [unknown] after [unknown] plays
* It is written in Python using the Keras interface to Tensorflow.

## Setup
* install python dependencies
   * `pip3 install keras tensorflow scikit-learn`
* set `LongPathsEnabled` to 1 in "registry editor" path: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem` (Windows)
* If your GPU supports CUDA, you can use anaconda to run the program with your GPU: https://www.anaconda.com/products/individual#Downloads
    * See tutorial: https://medium.com/@martin.berger/how-to-setup-gpu-accelerated-tensorflow-keras-on-windows-10-with-anaconda-3-bf844a720aa3
