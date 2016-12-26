Example: Generic Mach-Zehnder

this is a quite elaborate example. It shows good component design practice by first defining a generic component and the specializing it through inheritance. Here we define an MZI with e generic splitter and combiner, and a seperate component for each arm. 
the we specialize the component by making a MZI arm with a simple waveguide, but also making a specialized MZI with simple waveguides in both arms, and just a delay between both arms.
We then show that you can use both the generic component as well as the specialized ones to obtain the same result

To run the example, run 'execute.py' from the command line.

This example illustrates
- the use of inheritance
- the use of define_xxx methods to automatically calculate properties
- the use of Locked properties

 