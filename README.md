# LSD-LMSR
Liquidity Sensitive Dynamic LMSR


# Liquidity Sensitive Dynamic LMSR
This is a new Market Scoring Rule made for Zeitgeist Liquidity Pools.

## Content:
We have 2 main files:
1- lsdLMSRCoreFunctions.py --> contains the main functions for doing model calculations.

2- LSD-LMSR.py --> contains the simulation (this is the file that you need to execute).

3- requirements.txt --> install the necessary dependencies to run the simulation (we are using python 3). Disclaimer: it is possible that the pandas package might take a while. In case that you are using Debian, Ubuntu or MacOS, we recommend you to install it separately using: 
        `sudo apt-get install python3-pandas`

Once you install all the necessary dependencies with `pip install -r requirements.txt` or `pip3 install -r requirements.txt`, you are good to go! Inside the LSD-LMSR.py file, you will be able to modify some parameters to change the behaviour of your simulation.

## What you'll be able to modify into the simulation file LSD-LMSR.py (optional):
Into the LSD-LMSR.py file you could modify the following values:
- traderMaxFee: the maximum fee that a trader is willing to pay to make the transaction.
- b: proportion of the initial fee that the liquidity pool needs to ensure for the liquidity providers.
- q_1 and q_2: max volume that is  willing to assign to every asset.
- liquidityBounds: this defines the criteria to introduce bounds to the pool (the fees at this point elevates to the 50%. If you want to modify this, change the 0.5 to any value between 0 and 1 in line 103).
- 500 in line 71: represents the amount of time that a market signal (weight for buying or selling more of an asset than the other) remains the same.

## What you'll be able to modify into the core functions file lsdLMSRCoreFunctions.py (optional):
- z function: now we use a sigmoid function, but you can use whatever function that accomplish the following requirements:
      1- takes an r parameter equals to the ratio between the volume of a short period vs the volume of a larger period, 
      2- the first partial derivate of z and r is non-negative


## Simulation Mechanism:
After having observed and modified (or not) the general characteristics previously noted, the simulation will work as follows: first, a dictionary corresponding to the initial stage will be created; then a loop will start that will start making random decisions regarding which asset is going to be traded by traders. After deciding if this iteration will represent a buy or sell operation (determinated by a random choice with a change of possibilities for each asset that changes every 500 periods), this decision will be conditioned by a weight that will be interpreted as the interpretation of a market signal, which will change every 500 operations as well (loop iterations).

In each iteration, a random amount of this asset will be added to the pool, and this amount will be withdrawn from the maximum amount allocated for that asset.

If the pool has liquidity problems, the fee will increase drastically to discourage transactions, until this danger decreases.

The total iterations are equivalent to the total amount of transactions made in 4 seconds (block time). After finishing the simulation, a csv file will be generated with all the information of the transactions made in that period of time, and also some scatterplots to explore other relations of interest.
