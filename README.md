# Generals IO Simulator
The goal of this is to have a convenient way of simulating the 
game of [Generals IO](http://generals.io/) offline.

I personally plan on using it to train some form of AI.

I'm attempting to utilize as much code from [vzhou842's](https://github.com/vzhou842)
original in js. I dont speak js, so Im re-writing it in python as Im a parser tongue.

![Parser Tongue](https://i.imgur.com/f62NCWr.png)

# Installation
1. Get python 3.7
1. clone repo with: `git clone --recurse-submodules -j8 https://github.com/datavistics/generals_io_simulator.git`
1. go to proj_dir `cd generals_io_simulator`
1. if you forgot the full clone step run `git submodule update --init --recursive`
1. install requirements `pip install -r requirements.txt`

# Map Generation
Its not clear how to do this effectively, so I am scraping games from teh
first user I found with many 1v1 games - Spraget. 
