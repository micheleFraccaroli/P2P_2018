import networkx as nx
import matplotlib.pyplot as plt
import Util
from matplotlib.lines import Line2D

def toPlot(nodes, edges, sol_edges, num_sp, num_peer, mode):
	dict = {}
	G = nx.DiGraph()
	G.add_nodes_from(nodes)
	pos=nx.spring_layout(G)

	for i in edges:
		trovato = False
		for k in sol_edges:
			if(i == k):
				v1, v2 = i
				G.add_edge(v1,v2, color='orange',weight=3)
				trovato = True
		if(not trovato):
			v1, v2 = i
			G.add_edge(v1,v2, color='black', weight=2)

	edges = G.edges()
	colors = [G[u][v]['color'] for u,v in edges]
	weights = [G[u][v]['weight'] for u,v in edges]

	sizes = [800]
	colors_node = ['green']
	for n in range(num_sp):
		sizes.append(300)
		colors_node.append('red')
	for n2 in range(num_peer):
		sizes.append(100)
		colors_node.append('blue')

	nx.draw(G, pos, edges=edges, edge_color=colors, width=weights, with_labels=True, node_color=colors_node, node_size=sizes, font_size=10, font_color='black')

	nx.draw_networkx_edge_labels(G,pos, dict, clip_on=True)

	custom_lines = [Line2D([0], [0], marker ='o',color='green', markersize=10, lw=0),
                Line2D([0], [0], marker ='o',color='red', markersize=10, lw=0),
                Line2D([0], [0], marker ='o',color='blue', markersize=10, lw=0)]

	#fig, ax = plt.subplots()
	plt.legend(custom_lines, ['you', 'other superpeer', 'peer logged'])

	if(mode == "save"):
		plt.savefig("network_status.png")
	elif(mode == 'show'):
		plt.show()

if __name__ == '__main__':

	nodes = ['172.16.8.2','172.16.8.3','172.16.8.4','172.16.8.5']
	edges = [('172.16.8.2','172.16.8.4'),('172.16.8.2','172.16.8.3'),('172.16.8.5','172.16.8.2')]
	sol = [('172.16.8.2','172.16.8.4'),('172.16.8.2','172.16.8.3')]
	toPlot(nodes, edges, sol, 2, 2, "show")
