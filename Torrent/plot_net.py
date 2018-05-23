import random
import pylab
import matplotlib.pyplot as plt
from matplotlib.pyplot import pause
from matplotlib.lines import Line2D
import networkx as nx
import threading as th
#pylab.ion()

class plot_net:
    G = nx.Graph()
    pos = nx.spring_layout(G)
    fig, ax = plt.subplots(figsize=(7,5))
    t = 'Tracker'
    G.add_node(t)
    edges = []

    def addPeer(self, node, c):
        color = c
        self.ax.clear()
        self.G.add_node(node)
        self.G.add_edge(self.t, node, color='black')
        edges = self.G.edges()
        colors = [self.G[u][v]['color'] for u,v in edges]
        nx.draw(self.G, with_labels=True, node_color = c, node_shape="s", alpha=0.5, font_size=7, font_color='black')

        custom_lines = [Line2D([0], [0], marker ='o',color='black',alpha=0.5, markersize=8, lw=0),
                    Line2D([0], [0], marker ='o',color='green', alpha=0.5, markersize=8, lw=0)]

        plt.title('Tracker')
        plt.legend(custom_lines, ['Tracker', 'peer logged'])

    def removePeer(self, node, c):
        self.ax.clear()
        self.G.remove_node(node)
        nx.draw(self.G, with_labels=True, node_color = c, node_shape="s", alpha=0.5,font_size=7, font_color='black')

        custom_lines = [Line2D([0], [0], marker ='o',color='black',alpha=0.5, markersize=8, lw=0),
                    Line2D([0], [0], marker ='o',color='green', alpha=0.5, markersize=8, lw=0)]

        plt.title('Tracker')
        plt.legend(custom_lines, ['Tracker', 'peer logged'])

if __name__ == "__main__":    
    pn = plot_net()
    c = ['black']
    for i in range(10):
        c.append('green')
        pn.addPeer(i, c)
        pause(0.5)

    pause(5)
    pn.removePeer(3, c)
    pause(10.5)