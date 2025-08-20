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
| $6$ | | | | $\color{green}\text{0.008866310119628906 s (obj: 1)}$</br>$\color{green}\text{milp-model-1-CBC}$ | 
| $8$ | | | | $\color{green}\text{0.0505061149597168 s (obj: 1)}$</br>$\color{green}\text{milp-model-1-HiGHS}$ | 
| $10$ | | | | $\color{green}\text{0.10744023323059082 s (obj: 1)}$</br>$\color{green}\text{milp-model-1-CBC}$ | 
| $12$ | | | | $\color{green}\text{0.2605116367340088 s (obj: 1)}$</br>$\color{green}\text{milp-model-1-HiGHS}$ | 
| $14$ | | | | $\color{green}\text{0.38759803771972656 s (obj: 1)}$</br>$\color{green}\text{milp-model-1-CBC}$ | 
| $16$ | | | | $\color{green}\text{32.59202432632446 s (obj: 1)}$</br>$\color{green}\text{milp-model-1-CBC}$ | 
| $18$ | | | | $\color{lightgray}\text{Timeout}$ | 
| $20$ | | | | $\color{lightgray}\text{Timeout}$ | 

<!-- end-status -->
