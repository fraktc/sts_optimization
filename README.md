# Sports Scheduling Optimization

## Introduction

Project for the Combinatorial Decision Making and Optimization course at the University of Bologna (A.Y. 2024-2025).

## Description

Solving the sports scheduling problem using constraint programming (CP), propositional satisfiability (SAT), satisfiability modulo theories (SMT), and mixed-integer linear programming (MIP).

## Build

The experiments can be run through a Docker container. To build the container run:


cd src
docker build . -t cdmo --build-arg="AMPL_KEY=<ampl-community-key>"


## Execution

To perform all the experiments, run:

docker run -v ./res:/cdmo/results cdmo
--timeout=<timeout-per-model>
[--mem-limit=<ram-limit>]
[--verbose]


To run a specific model of a specific method on a specific instance, run:

docker run -v ./res:/cdmo/results cdmo
--timeout=<timeout-per-model>
--methods=<method-name>
--models=<model-name>
--instances=<instance-number>
[--mem-limit=<ram-limit>]
[--verbose]


## Results
<!-- Do NOT remove the comments below -->
<!-- begin-status -->
| Instance | [CP](./method-statuses/cp-status.md) | [SAT](./method-statuses/sat-status.md) | [SMT](./method-statuses/smt-status.md) | [MIP](./method-statuses/mip-status.md) |
|:-:| :---:|:---:|:---:|:---:|
| $4$ | | $\color{red}\text{Inconsistent}$ | | | 
| $6$ | | $\color{green}\text{0.11846923828125 s (obj: 0)}$</br>$\color{green}\text{optimizer-z3-z3}$ | | | 
| $8$ | | $\color{green}\text{0.48363542556762695 s (obj: 0)}$</br>$\color{green}\text{optimizer-z3-z3}$ | | | 
| $10$ | | $\color{orange}\text{2.901758909225464 s (obj: 3)}$</br>$\color{orange}\text{solver-heule-sequential}$ | | | 
| $12$ | | $\color{orange}\text{25.762351274490356 s (obj: 3)}$</br>$\color{orange}\text{solver-pairwise-sequential}$ | | | 
| $14$ | | $\color{orange}\text{55.34747576713562 s (obj: 5)}$</br>$\color{orange}\text{solver-bitwise-pairwise}$ | | | 
| $16$ | | | | | 
| $18$ | | | | | 
| $20$ | | | | | 

<!-- end-status -->
