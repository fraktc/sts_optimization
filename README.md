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
| $4$ | | $\color{lightgray}\text{Timeout}$ | $\color{red}\text{Inconsistent}$ | | 
| $6$ | | $\color{red}\text{Inconsistent}$ | $\color{red}\text{Inconsistent}$ | | 
| $8$ | | $\color{red}\text{Inconsistent}$ | $\color{red}\text{Inconsistent}$ | | 
| $10$ | | $\color{red}\text{Inconsistent}$ | | | 
| $12$ | | $\color{lightgray}\text{Timeout}$ | | | 
| $14$ | | $\color{lightgray}\text{Timeout}$ | | | 
| $16$ | | $\color{lightgray}\text{Timeout}$ | | | 
| $18$ | | $\color{lightgray}\text{Timeout}$ | | | 
| $20$ | | $\color{lightgray}\text{Timeout}$ | | | 

<!-- end-status -->
