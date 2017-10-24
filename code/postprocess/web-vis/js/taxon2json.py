'''
    from taxonomy_ids.txt to json
'''
import json
import os
import re

'''
    Example Line:
    1_1_1	*/large_scale_distributed_systems	large_scale_distributed_systems,software_engineering,agile_development,software_development,software_process_improvement,software_process,agile_methods,requirements_engineering,web_services,software_reuse
'''
links = []
nodes = dict()
id2path = {}
cnt = 1
with open('TaxonGen/data/semantic_scholar_eecs/taxonomy_ids.txt') as f:
    for line in f:
        meta = re.split(pattern='\t', string=line)
        taxonID = meta[0]
        path_raw = meta[1][2:]
        path = path_raw.rsplit('/', 1)

        if not path:
            continue
        id2path[cnt] = path_raw
        level = taxonID[0]
        nodes[path_raw] = {
            'taxonID': taxonID,
            'level': level,
            'path': meta[1][2:],
            'keywords': meta[2].strip().split(','),
            'name': path[-1]
        }
        if len(path) >= 2:
            links.append((path[0], path_raw))
        cnt += 1

deduplicate_links = []
for link in links:
    if link[0] == link[1]:
        continue
    if link not in deduplicate_links:
        deduplicate_links.append(link)
links = deduplicate_links

# print links

#
root_name = 'semantic_scholar'
nodes[root_name] = {
    'taxonID': '0-0-0',
    'level': 0,
    'path': root_name,
    'name': root_name,
    'keywords': ['computer_science', 'electrical_engineering']
}

parents, children = zip(*links)
root_nodes = {x for x in parents if x not in children and len(x.split('/')) == 1}
for node in root_nodes:
    links.append((root_name, node))

# print links

def get_nodes(node):
    # d = {}
    # d['name'] = node
    d = nodes[node].copy()
    children = get_children(node)
    if children:
        d['children'] = [get_nodes(child) for child in children]
    return d


def get_children(node):
    return [x[1] for x in links if x[0] == node]


tree = get_nodes(root_name)
print json.dumps(tree, indent=4)
# with open('TaxonGen/data/semantic_scholar_eecs/tree.json', 'w') as f:
#     json.dump(tree, f)
# with open('TaxonGen/data/semantic_scholar_eecs/id2path.json', 'w') as f:
#     json.dump(id2path, f)
# cp TaxonGen/data/semantic_scholar_eecs/tree.json webUI/static/
# cp TaxonGen/data/semantic_scholar_eecs/id2path.json webUI/static/
