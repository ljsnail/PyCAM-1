#!/usr/bin/env python
import graph

g = graph.Graph()
g.read_file('6.txt')
g.display()
edges = g.goemans()
