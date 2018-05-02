import networkx as nx
import matplotlib.pyplot as plt

def toPlot(nodes, edges, sol_edges):
	dict = {}
	G = nx.Graph()
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

	nx.draw(G, pos, edges=edges, edge_color=colors, width=weights,with_labels=True, node_color='r', node_size=400, font_size=10, font_color='black')

	nx.draw_networkx_edge_labels(G,pos, dict, clip_on=True)

	plt.savefig("network_status.png")
	#plt.show()

if __name__ == '__main__':

	nodes = ['172.16.8.2','172.16.8.3','172.16.8.4','172.16.8.5']
	edges = [('172.16.8.2','172.16.8.4'),('172.16.8.2','172.16.8.3'),('172.16.8.5','172.16.8.2')]
	sol = [('172.16.8.2','172.16.8.4'),('172.16.8.5','172.16.8.2')]
	toPlot(nodes, edges, sol)
