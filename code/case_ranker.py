'''
__author__: Fangbao Tao
__description__: Main function for CaseOLAP
  Current we use a sim version of CaseOLAP
__latest_updates__: 09/26/2017
'''
import argparse
import utils
import operator


def read_caseolap_result(case_file):
    phrase_map = {}
    cell_map = {}

    cell_cnt = 0
    with open(case_file) as f:
        for line in f:
            cell_cnt += 1
            segments = line.strip('\r\n ').split('\t')
            cell_id, phs_str = segments[0], segments[1][1:-1]
            cell_map[cell_id] = []
            segments = phs_str.split(', ')
            for ph_score in segments:
                parts = ph_score.split('|')
                ph, score = parts[0], float(parts[1])
                if ph not in phrase_map:
                    phrase_map[ph] = {}
                phrase_map[ph][cell_id] = score
                cell_map[cell_id].append((ph, score))

    return phrase_map, cell_map, cell_cnt


def rank_phrase(case_file):
    ph_dist_map = {}
    smoothing_factor = 0.0

    phrase_map, cell_map, cell_cnt = read_caseolap_result(case_file)
    print(cell_cnt)
    unif = [1.0 / cell_cnt] * cell_cnt

    for ph in phrase_map:
        ph_vec = [x[1] for x in phrase_map[ph].items()]
        if len(ph_vec) < cell_cnt:
            ph_vec += [0] * (cell_cnt - len(ph_vec))
        # smoothing
        ph_vec = [x + smoothing_factor for x in ph_vec]
        ph_vec = utils.l1_normalize(ph_vec)
        ph_dist_map[ph] = utils.kl_divergence(ph_vec, unif)

    ranked_list = sorted(list(ph_dist_map.items()), key=operator.itemgetter(1), reverse=True)

    return ranked_list


def write_keywords(o_file, ranked_list, thres):
    with open(o_file, 'w+') as g:
        for ph in ranked_list:
            if ph[1] > thres:
                g.write('%s\n' % (ph[0]))
    tmp_file = o_file + '-score.txt'
    with open(tmp_file, 'w+') as g:
        for ph in ranked_list:
            g.write('%s\t%f\n' % (ph[0], ph[1]))


def main_rank_phrase(input_f, output_f, thres):
    ranked_list = rank_phrase(input_f)
    write_keywords(output_f, ranked_list, thres)
    print("[CaseOLAP] Finish pushing general terms up")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='case_ranker.py', \
                                     description='Ranks the distinctiveness score using caseolap result.')
    parser.add_argument('-folder', required=True, \
                        help='The folder that stores the file.')
    parser.add_argument('-iter', required=True, \
                        help='Iteration index.')
    parser.add_argument('-thres', required=True, \
                        help='The files used.')
    args = parser.parse_args()

    input_f = '%s/caseolap-%s.txt' % (args.folder, args.iter)
    output_f = '%s/keywords-%s.txt' % (args.folder, args.iter)

    main_rank_phrase(input_f, output_f, float(args.thres))
