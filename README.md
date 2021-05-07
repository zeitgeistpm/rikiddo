# LSD-LMSR
Liquidity Sensitive Dynamic LMSR


# Liquidity Sensitive Dynamic LMSR
This is a new Market Scoring Rule made for Zeitgeist Liquidity Pools.

##Content:
We have 2 main files:
1- lsdLMSRCoreFunctions.py --> contains the main functions for doing model calculations.
2- LSD-LMSR.py --> contains the simulation (this is the file that you need to execute).

Into the LSD-LMSR.py file you'll need to modify:
- traderMaxFee: the maximum fee that a trader is willing to pay to make the transaction.
- b: proportion of the initial fee that the liquidity pool needs to ensure for the liquidity providers.
- q_1 and q_2: initial volume of the assets
- liquidityBounds: this defines the criteria to introduce bounds to the pool (the fees at this point elevates to the 50%. If you want to modify this, change the 0.5 to any value between 0 and 1 in line 103)
