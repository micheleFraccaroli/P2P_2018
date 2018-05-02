import networkx as nx
import matplotlib.pyplot as plt
import Util

def toPlot(nodes, edges, sol_edges, num_sp, num_peer):
	dict = {}
	G = nx.DiGraph()
	G.add_nodes_from(nodes)
	pos=nx.spring_layout(G)

	for ip in nodes:
		ipv = Util.ip_deformatting()

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

	sizes = [500]
	for n in range(num_sp):
		sizes.append(300)
	for n2 in range(num_peer):
		sizes.append(100)

	nx.draw(G, pos, edges=edges, edge_color=colors, width=weights, with_labels=True, node_color='r', node_size=sizes, font_size=10, font_color='black')

	nx.draw_networkx_edge_labels(G,pos, dict, clip_on=True)

	plt.savefig("network_status.png")
	#plt.show()

if __name__ == '__main__':

	nodes = ['172.16.8.2','172.16.8.3','172.16.8.4','172.16.8.5']
	edges = [('172.16.8.2','172.16.8.4'),('172.16.8.2','172.16.8.3'),('172.16.8.5','172.16.8.2')]
	sol = [('172.16.8.2','172.16.8.4'),('172.16.8.5','172.16.8.2')]
	toPlot(nodes, edges, sol)
