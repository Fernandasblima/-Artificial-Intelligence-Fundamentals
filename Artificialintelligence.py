
import os
import matplotlib
matplotlib.use('Agg')  

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

os.makedirs('docs', exist_ok=True)

dados = {
    'bairro': ['Centro', 'Jardim', 'Industrial', 'São Pedro', 'Vila Nova', 'Alvorada', 'Santa Clara', 'Bela Vista', 'Rosário', 'Cruzeiro'],
    'x': [5, 7, 3, 8, 2, 9, 1, 6, 4, 10],
    'y': [5, 8, 2, 9, 3, 10, 1, 6, 4, 11]
}
df = pd.DataFrame(dados)
print("Dataframe carregado:")
print(df)

#  grafo
def criar_grafo():
    G = nx.Graph()
    conexoes = [
        ('Centro', 'Jardim', 5),
        ('Centro', 'Industrial', 8),
        ('Jardim', 'São Pedro', 4),
        ('Industrial', 'Vila Nova', 6),
        ('São Pedro', 'Alvorada', 7),
        ('Vila Nova', 'Santa Clara', 5),
        ('Santa Clara', 'Rosário', 6),
        ('Rosário', 'Cruzeiro', 2),
        ('Cruzeiro', 'Bela Vista', 4),
        ('Bela Vista', 'Alvorada', 3),
        ('Centro', 'Rosário', 6)
    ]
    for origem, destino, tempo in conexoes:
        G.add_edge(origem, destino, weight=tempo)
    return G

# Função que calcula A* e salva imagem do grafo com caminho destacado
def mostrar_rota_salvar(origem, destino, filename='docs/rota.png'):
    G = criar_grafo()

    if not nx.has_path(G, origem, destino):
        print(f"Não existe caminho entre {origem} e {destino}.")
        return

    caminho = nx.astar_path(G, origem, destino, weight='weight')
    tempo_total = nx.astar_path_length(G, origem, destino, weight='weight')
    print(f"Caminho mais curto entre {origem} e {destino}: {caminho}")
    print(f"Tempo total estimado: {tempo_total} minutos")

    pos = nx.spring_layout(G, seed=42)
    edge_labels = nx.get_edge_attributes(G, 'weight')

    plt.figure(figsize=(8,6))
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='skyblue', edgecolors='black')
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')

    path_edges = list(zip(caminho, caminho[1:]))
    edge_colors = ['red' if (u, v) in path_edges or (v, u) in path_edges else 'black' for u, v in G.edges()]

    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    plt.title(f"Caminho mais curto de {origem} até {destino} (em vermelho)")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filename, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Figura salva em: {filename}")

# K-Means 
def aplicar_kmeans_salvar(n_clusters=3, filename='docs/cluster.png'):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(df[['x', 'y']])
    score = silhouette_score(df[['x', 'y']], df['cluster'])
    print(f"Silhouette Score: {score:.2f}")

    plt.figure(figsize=(7,6))
    plt.scatter(df['x'], df['y'], c=df['cluster'])
    for i, bairro in enumerate(df['bairro']):
        plt.text(df['x'][i] + 0.1, df['y'][i] + 0.1, bairro, fontsize=9)
    plt.title(f'Agrupamento de Entregas (k={n_clusters})')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.tight_layout()
    plt.savefig(filename, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Figura do agrupamento salva em: {filename}")

# A*
def a_star_por_cluster_salvar():
    G = criar_grafo()
    relatorio = []
    for cluster_id in df['cluster'].unique():
        bairros_cluster = df[df['cluster'] == cluster_id]['bairro'].tolist()
        relatorio.append(f"\nCluster {cluster_id} - Bairros: {bairros_cluster}")
        origem = bairros_cluster[0]
        for destino in bairros_cluster[1:]:
            if nx.has_path(G, origem, destino):
                caminho = nx.astar_path(G, origem, destino, weight='weight')
                tempo = nx.astar_path_length(G, origem, destino, weight='weight')
                relatorio.append(f"  {origem} → {destino}: {caminho} | Tempo: {tempo} min")
            else:
                relatorio.append(f"  {origem} → {destino}: Sem caminho disponível")
  
    with open('docs/relatorio_clusters.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(relatorio))
    print("Relatório dos caminhos por cluster salvo em: docs/relatorio_clusters.txt")


if __name__ == "__main__":
    mostrar_rota_salvar('Cruzeiro', 'Vila Nova', filename='docs/rota_cruzeiro_vilanova.png')
    aplicar_kmeans_salvar(n_clusters=3, filename='docs/cluster.png')
    a_star_por_cluster_salvar()
    print("Execução finalizada. Abra os arquivos dentro da pasta 'docs'.")
