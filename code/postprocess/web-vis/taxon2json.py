'''
    from taxonomy_ids.txt to json
'''
import json
import argparse
import re

'''
    Example Line:
    1_1_1	*/large_scale_distributed_systems	large_scale_distributed_systems,software_engineering,agile_development,software_development,software_process_improvement,software_process,agile_methods,requirements_engineering,web_services,software_reuse
'''

def main(args):
  def get_children(node):
    return [x[1] for x in links if x[0] == node]

  def get_nodes(node):
    d = nodes[node].copy()
    children = get_children(node)
    if children:
      d['children'] = [get_nodes(child) for child in children]
    return d

  links = []
  nodes = dict()
  id2path = {}
  cnt = 1
  inputFilePath = args.input

  with open(inputFilePath, "r") as f:
    for line in f:
      meta = re.split(pattern='\t', string=line)
      taxonID = meta[0]
      path_raw = meta[1][2:]
      path = path_raw.rsplit('/', 1)

      if not path:
        continue
      id2path[cnt] = path_raw
      level = taxonID[0]
      nodes[path_raw] = {'taxonID': taxonID, 'level': level, 'path': meta[1][2:],
        'keywords': meta[2].strip().split(','), 'name': path[-1]}
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

  root_name = 'root'
  nodes[root_name] = {'taxonID': '0-0-0', 'level': 0, 'path': root_name, 'name': root_name,
    'keywords': ['computer_science']}

  parents, children = zip(*links)
  root_nodes = {x for x in parents if x not in children and len(x.split('/')) == 1}
  for node in root_nodes:
    links.append((root_name, node))

  tree = get_nodes(root_name)
  print(json.dumps(tree, indent=4))

  with open("./tree.json", "w") as fout:
    json.dump(tree, fout)




if __name__ == '__main__':
  # python3 taxon2json.py -input ./sample_taxonomy.txt
  parser = argparse.ArgumentParser(prog='taxon2json.py',
                                   description='Convert TaxonGen output to json file for visualization.')
  parser.add_argument('-input', required=True, help='Input path of taxonomy')
  args = parser.parse_args()
  main(args)