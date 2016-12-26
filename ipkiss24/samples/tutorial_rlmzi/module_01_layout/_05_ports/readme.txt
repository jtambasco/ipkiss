Example: Ports

In this example we add Ports to our ring resonator. Ports define where the input and output waveguides of the Structure are located, and what the waveguide definition (cross section) is at that location  

To run the example, run 'execute.py' from the command line.

This example illustrates
- how to use the define_ports method to add ports
- that an OpticalPort has a position, an angle (in degrees) and a waveguide definition
- that ports point outward
- that a subset of the ports can be queries with methods as 'east_ports'
- that ports can be addressed using a shorthand indexing such as "E0"

 