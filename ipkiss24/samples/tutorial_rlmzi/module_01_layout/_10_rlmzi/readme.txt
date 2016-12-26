Example: Ring Loaded Mach Zehnder

In this example we combine our directional coupler with our rings to make a Ring-Loaded Mach-Zehnder Interferometer. We use safe margins to place the splitter and combiner and the two rings and automatically generate routes between the correct ports.

To run the example, run 'execute.py' from the command line.

This example illustrates
- the use of the size_info object to estimate space a component needs
- some basic rules for placement
- how routes can be concatenated
- more use of transformations

Note: While this example generates a nice-looking MZI, it lacks any information about the exact length of both arms, which is of course essential in an MZI. The next example addresses this.

 