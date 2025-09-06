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
<<<<<<< HEAD
| $4$ | $\color{lightgray}\text{Timeout}$ | $\color{lightgray}\text{Timeout}$ | | | 
| $6$ | $\color{green}\text{0 s (obj: 1)}$</br>$\color{green}\text{RR-CP-plain-chuffed}$ | $\color{red}\text{Inconsistent}$ | | | 
| $8$ | $\color{green}\text{0 s (obj: 1)}$</br>$\color{green}\text{RR-CP-plain-chuffed}$ | $\color{red}\text{Inconsistent}$ | | | 
| $10$ | $\color{green}\text{0 s (obj: 1)}$</br>$\color{green}\text{RR-CP-plain-chuffed}$ | $\color{red}\text{Inconsistent}$ | | | 
| $12$ | $\color{green}\text{0 s (obj: 1)}$</br>$\color{green}\text{RR-CP-plain-chuffed}$ | $\color{lightgray}\text{Timeout}$ | | | 
| $14$ | $\color{green}\text{0 s (obj: 1)}$</br>$\color{green}\text{RR-CP-symm-chuffed}$ | $\color{lightgray}\text{Timeout}$ | | | 
| $16$ | $\color{green}\text{2 s (obj: 1)}$</br>$\color{green}\text{RR-CP-symm-chuffed}$ | $\color{lightgray}\text{Timeout}$ | | | 
| $18$ | $\color{green}\text{1 s (obj: 1)}$</br>$\color{green}\text{RR-CP-symm-chuffed}$ | $\color{lightgray}\text{Timeout}$ | | | 
| $20$ | $\color{green}\text{67 s (obj: 1)}$</br>$\color{green}\text{RR-CP-symm-chuffed}$ | $\color{lightgray}\text{Timeout}$ | | | 
=======
| $4$ | $\color{pink}\text{Crashed}$ | $\color{lightgray}\text{Timeout}$ | | | 
| $6$ | $\color{pink}\text{Crashed}$ | $\color{red}\text{Inconsistent}$ | | | 
| $8$ | $\color{pink}\text{Crashed}$ | $\color{red}\text{Inconsistent}$ | | | 
| $10$ | $\color{pink}\text{Crashed}$ | $\color{red}\text{Inconsistent}$ | | | 
| $12$ | $\color{pink}\text{Crashed}$ | $\color{lightgray}\text{Timeout}$ | | | 
| $14$ | $\color{pink}\text{Crashed}$ | $\color{lightgray}\text{Timeout}$ | | | 
| $16$ | $\color{pink}\text{Crashed}$ | $\color{lightgray}\text{Timeout}$ | | | 
| $18$ | $\color{pink}\text{Crashed}$ | $\color{lightgray}\text{Timeout}$ | | | 
| $20$ | $\color{pink}\text{Crashed}$ | $\color{lightgray}\text{Timeout}$ | | | 
>>>>>>> main

<!-- end-status -->
