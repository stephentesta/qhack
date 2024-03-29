#! /usr/bin/python3

import sys
import pennylane as qml
import numpy as np


def gradient_200(weights, dev):
    r"""This function must compute the gradient *and* the Hessian of the variational
    circuit using the parameter-shift rule, using exactly 51 device executions.
    The code you write for this challenge should be completely contained within
    this function between the # QHACK # comment markers.

    Args:
        weights (array): An array of floating-point numbers with size (5,).
        dev (Device): a PennyLane device for quantum circuit execution.

    Returns:
        tuple[array, array]: This function returns a tuple (gradient, hessian).

            * gradient is a real NumPy array of size (5,).

            * hessian is a real NumPy array of size (5, 5).
    """

    @qml.qnode(dev, interface=None)
    def circuit(w):
        for i in range(3):
            qml.RX(w[i], wires=i)

        qml.CNOT(wires=[0, 1])
        qml.CNOT(wires=[1, 2])
        qml.CNOT(wires=[2, 0])

        qml.RY(w[3], wires=1)

        qml.CNOT(wires=[0, 1])
        qml.CNOT(wires=[1, 2])
        qml.CNOT(wires=[2, 0])

        qml.RX(w[4], wires=2)

        return qml.expval(qml.PauliZ(0) @ qml.PauliZ(2))

    gradient = np.zeros([5], dtype=np.float64)
    hessian = np.zeros([5, 5], dtype=np.float64)

    # QHACK #
    print("Weights", weights)
    same_value = 2 * circuit(weights)
    for i in range(5): 
        shifted = weights.copy() 
        shifted[i] += np.pi/2 

        forward = circuit(shifted) # forward evaluation 

        shifted[i] -= np.pi 
        backward = circuit(shifted) # backward evaluation 

        grad = 0.5 * (forward - backward) 
        gradient[i] = grad # assign gradient 
       
        hess = 0.5 * (forward + backward - same_value)
        hessian[i,i] = hess 
        print("Hessian", hessian[i][i])
        for j in range(i+1, 5): 
            # create standard basis vectors 
            standard_i = np.zeros(5) 
            standard_i[i] = 1.0 
            standard_j = np.zeros(5) 
            standard_j[j] = 1.0 
            
            hessian[i, j] = (circuit(weights + np.pi/2 *(standard_i + standard_j))
            - circuit(weights + np.pi/2 * (-1*standard_i + standard_j))
            - circuit(weights + np.pi/2 * (standard_i - standard_j)) 
            + circuit(weights - np.pi/2 * (standard_i + standard_j)))/4
        
        # Fix matrix size 
        hessian = hessian + hessian.T - np.diag(np.diag(hessian))
       # QHACK #

    return gradient, hessian, circuit.diff_options["method"]


if __name__ == "__main__":
    # DO NOT MODIFY anything in this code block
    weights = sys.stdin.read()
    weights = weights.split(",")
    weights = np.array(weights, float)

    dev = qml.device("default.qubit", wires=3)
    gradient, hessian, diff_method = gradient_200(weights, dev)

    print(
        *np.round(gradient, 10),
        *np.round(hessian.flatten(), 10),
        dev.num_executions,
        diff_method,
        sep=","
    )
