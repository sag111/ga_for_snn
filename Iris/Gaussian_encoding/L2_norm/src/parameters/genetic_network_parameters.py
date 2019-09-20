"""
The parameters used in genetic.py,
except those that are given directly to MultiNEAT.
The latter are in traits.py.
"""

# The structure of a network inside MultiNEAT.
# As soon as only global SNN parameters are
# adjusted genetically, these inputs and outputs numbers
# do not matter.
# Change inputs_number to 100 and outputs_number to 3
# when each neuron or synapse will be made to evolve independently.
inputs_number = 1
outputs_number = 1

# for how long to simulate
max_generations = 100
# [epochs], how frequently to save the best network and its output
result_watching_step = 1

