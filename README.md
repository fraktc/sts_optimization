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
| Instance | [CP](./method-statuses/cp-status.md) | [SAT](./method-statuses/sat-status.md) | [SMT](./method-statuses/smt-status.md) | [MILP](./method-statuses/milp-status.md) |
|:-:| :---:|:---:|:---:|:---:|
| $4$ | | | | $\color{lightgray}\text{Timeout}$ | 
| $6$ | | | | $\color{green}\text{0.0093 s (obj: 1)}$</br>$\color{green}\text{milp-model-3-CBC}$ | 
| $8$ | | | | $\color{green}\text{0.0149 s (obj: 1)}$</br>$\color{green}\text{milp-model-4-CBC}$ | 
| $10$ | | | | $\color{green}\text{0.0256 s (obj: 1)}$</br>$\color{green}\text{milp-model-3-CBC}$ | 
| $12$ | | | | $\color{green}\text{0.2429 s (obj: 1)}$</br>$\color{green}\text{milp-model-1-CBC}$ | 
| $14$ | | | | $\color{green}\text{16.2076 s (obj: 1)}$</br>$\color{green}\text{milp-model-4-CBC}$ | 
| $16$ | | | | | 
| $18$ | | | | | 
| $20$ | | | | | 

<!-- end-status -->
