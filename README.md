

# SI2 - Mini-projecto nº 2
Este mini-projecto está centrado na matéria de aprendizagem por reforço, tendo por aplicação o jogo "Bomberman".

Na disciplina de Inteligência Artificial (IA), seguindo o enunciado "bomberman.pdf", os alunos desenvolveram agentes para jogar este jogo autonomamente. Foram fornecidos o motor do jogo ("server.py") e um visualizador ("viewer.py") e os alunos apresentaram agentes, um dos quais é agora fornecido a título exemplificativo ("student.py").

Em IA, estes agentes eram tipicamente pré-programados, ou seja, não usavam mecanismos da área da aprendizagem automática.

Agora, neste mini-projecto de SI2, os alunos devem desenvolver agentes que, recorrendo a aprendizagem por reforço, consigam adquirir a funcionalidade necessária para jogar o jogo do Bomberman.

![Demo](https://github.com/dgomes/iia-ia-bomberman/raw/master/data/DemoBomberman.gif)

## How to install

Make sure you are running Python 3.5 or higher.

`$ pip install -r requirements.txt`

*Tip: you might want to create a virtualenv first*

## Repository organization

In our project, we developed 3 different methods, each with different rewards and strategies for the agent.

Each approach has its own folder with all the files necessary to run the agent. There are 3 files common to every approach:

 -  reinforcementAgentAI.py : This file has the class where the agent and the functions used by the agent are defined.
 -  reinforcementSearchNode.py : This file has the class where a node is defined.
 -  reinforcementStudent.py : This file is where the agent is instantiated and used to play the game.

In addition to these files, in approaches 1 and 2, there are 2 extra files:

-  reinforcementConsts.py : This file has constants and enums used by other files.
-  reinforcementUtils.py : This file has some useful functions that are used in other files.

In the Deliverables folder, the presentation and report made for this project can be found.

## How to run

Start the server

`$ python3 server.py`

Start the viewer

`$ python3 viewer.py`

Go to the folder of the chosen approach

`$ cd ApproachX`

Start the agent

`$ python3 reinforcementStudent.py`

## Debug Installation

Make sure pygame is properly installed:

python -m pygame.examples.aliens

# Tested on:
- Ubuntu 18.04
- OSX 10.14.6
- Windows 10.0.18362

