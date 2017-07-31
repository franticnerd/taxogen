from graphviz import Digraph


def load_nodes(node_file, min_level=1, max_level=3, prefix='*'):
    nodes = {'*':[]}
    with open(node_file, 'r') as f:
        for line in f:
            items = line.strip().split('\t')
            node_id = items[0]
            node_content = items[1].split(',')[:8]
            nodes[node_id] = node_content
    prune_nodes = {}
    for node_id, node_content in nodes.items():
        # prune nodes
        if not node_id.startswith(prefix):
            continue
        level = len(node_id.split('/'))
        if not min_level <= level <= max_level:
            continue
        if level == min_level:
            node_content = []
        prune_nodes[node_id] = node_content
    return prune_nodes


def gen_edges(nodes):
    node_ids = nodes.keys()
    node_ids.sort(key=lambda x: len(x))
    edges = []
    for i in xrange(len(nodes) - 1):
        for j in xrange(i+1, len(nodes)):
            if is_parent(node_ids[i], node_ids[j]):
                edges.append([node_ids[i], node_ids[j]])
    return edges


def is_parent(node_a, node_b):
    if not node_b.startswith(node_a):
        return False
    items_a = node_a.split('/')
    items_b = node_b.split('/')
    if len(items_b) - len(items_a) == 1:
        return True
    else:
        return False


def gen_node_label(node_id, node_content):
    node_name = node_id.split('/')[-1]
    keywords = '\\n'.join(node_content)
    if len(node_content) == 0:
        return node_name
    else:
        return '{%s|%s}' % (node_name, keywords)


def draw(nodes, edges, output_file):
    d = Digraph(node_attr={'shape': 'record'})
    for node_id, node_content in nodes.items():
        d.node(node_id, gen_node_label(node_id, node_content))
    for e in edges:
        d.edge(e[0], e[1])
    d.render(filename=output_file)

def main(node_file, output_file, min_level, max_level, prefix='*'):
    nodes = load_nodes(node_file, min_level, max_level, prefix)
    edges = gen_edges(nodes)
    draw(nodes, edges, output_file)

tax_dir = '/Users/chao/data/projects/local-embedding/dblp/taxonomies/'
img_dir = '/Users/chao/data/projects/local-embedding/dblp/draw_tax/'

main(tax_dir + 'ours.txt', img_dir + 'l1-our', min_level=1, max_level=2)
main(tax_dir + 'hc.txt', img_dir + 'l1-hc', min_level=1, max_level=2)
main(tax_dir + 'no-caseolap.txt', img_dir + 'l1-no-case', min_level=1, max_level=2)
main(tax_dir + 'hlda.txt', img_dir + 'l1-hlda', min_level=1, max_level=2)
main(tax_dir + 'hpam.txt', img_dir + 'l1-hpam', min_level=1, max_level=2)

main(tax_dir + 'ours.txt', img_dir + 'l2-ir-our', min_level=2, max_level=3, prefix='*/information_retrieval')
main(tax_dir + 'hc.txt', img_dir + 'l2-ir-hc', min_level=2, max_level=3, prefix='*/information_retrieval')
main(tax_dir + 'no-localembedding.txt', img_dir + 'l2-ir-no-local', min_level=2, max_level=3, prefix='*/information_retrieval')
main(tax_dir + 'no-caseolap.txt', img_dir + 'l2-ir-no-case', min_level=2, max_level=3, prefix='*/information_retrieval')
main(tax_dir + 'hlda.txt', img_dir + 'l2-ir-hlda', min_level=2, max_level=3, prefix='*/1')

main(tax_dir + 'ours.txt', img_dir + 'l2-ml-our', min_level=2, max_level=3, prefix='*/learning_algorithms')
main(tax_dir + 'no-localembedding.txt', img_dir + 'l2-ml-no-le', min_level=2, max_level=3, prefix='*/learning_algorithms')
main(tax_dir + 'no-caseolap.txt', img_dir + 'l2-ml-no-case', min_level=2, max_level=3, prefix='*/learning_algorithms')
main(tax_dir + 'hc.txt', img_dir + 'l2-ml-hc', min_level=2, max_level=3, prefix='*/learning_algorithms')


main(tax_dir + 'ours.txt', img_dir + 'l3-nn-our', min_level=3, max_level=4, prefix='*/learning_algorithms/neural_networks')
main(tax_dir + 'no-localembedding.txt', img_dir + 'l3-nn-no-le', min_level=3, max_level=4, prefix='*/learning_algorithms/neural_networks')

# def f():
#     dot.node('A', '{one | two \\n three}')
#     dot.node('B', '{<f0> what |<f1> Sir\n Bedevere \n the Wise}')
#     dot.node('L', '|G|')
#     dot.edges(['AB', 'AL'])
#     # dot.edge('B', 'L', constraint='false')
#     dot.render('./round-table.pdf', view=True)
#     print dot.source
