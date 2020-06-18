# animal-guesser
This project was developed in the scope of the Postgraduate in Applied Artificial Intelligence at the Erasmushogeschool Brussel, for the Intelligent Interfaces course. The task was to develop an application combining multiple sensory interfaces of a computer. Here, we choose to use Speech Recognition and NLP as the brain aspects of our application.

## Description

This project was inspired by the famous Taboo game. As a reminder, the Taboo game is a board game where a player picks a card with a word that he needs to describe in order to make the other players guess what the word is. The player has 30s and cannot say 3 « taboo » words in his description. If he does, he looses the game. The goal of the player is to make the other players of his team guess as many cards as possible. 

This version is different. Here the goal of the player is to make an AI guess the word he is describing. 

## Requirements

You need the following libraries installed in order to enjoy the functionalities of the game:
- **PyAudio** (https://pypi.org/project/PyAudio/)
- **SpeechRecognition** (https://pypi.org/project/SpeechRecognition/): if « device_index » is unspecified or « None », the default microphone is used as the audio source. Otherwise, « device_index » should be the index of the device to use for audio input. A device index is an integer between 0 and « pyaudio.get_device_count() - 1 » (assume we have used « import pyaudio » beforehand) inclusive. It represents an audio device such as a microphone or speaker. See the [PyAudio](http://people.csail.mit.edu/hubert/pyaudio/docs/) documentation for more details.

- **ElasticSearch** (https://pypi.org/project/elasticsearch/)
- **Scikit-learn** (https://pypi.org/project/scikit-learn/)

## Workflow
![alt text](https://github.com/NsrWissam/animal-guesser/blob/cwaltregny-dev-1/.idea/workflow.001.jpeg?raw=true)
