from __future__ import print_function
from collections import defaultdict
import numpy as np

'''
Expectation
compute forward and backward probabilities
then return fractional counts of each alignment

wordPairs:  (string, string) of English, Japanese
prior:      dict mapping e->j->p where p is current prob. est.
maxE2J:     maximum k in k-to-1 mapping
'''
def Expectation(wordPairs, prior, maxE2J):
    fracCount = {}
    for i in range(len(wordPairs)):
        eword = wordPairs[i][0]
        jword = wordPairs[i][1]
        e, j = eword.split(), jword.split()
        # compute forward and backward prob for each word
        alpha = Forward(e, j, prior, maxE2J)
        beta = Backward(e, j, prior, maxE2J)

        # sum the fractional counts
        fracCount[i] = FindFracCounts(e, j, alpha, beta, prior, maxE2J)

    return fracCount


'''
FindFracCounts
eprons:     list of English sounds
jprons:     list of Japanese sounds
alpha:      array of forward probabilities by [epron][jpron]
beta:       array of backward probabilities
prior:      dict mapping e->j->p where p is current prob. est.
maxE2J:     maximum k in k-to-1 mapping
'''


def FindFracCounts(eprons, jprons, alpha, beta, prior, maxE2J):
    numJ, numE = len(jprons), len(eprons)
    # counts = defaultdict(lambda : defaultdict(float))



    eplison = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

    for i in range(1,numE+1):
        prev_alpha = np.array(alpha[i])
        cur_alpha = np.array(alpha[i - 1])

        cur_indexes = list(np.where(prev_alpha > 0)[0])
        pre_indexes = list(np.where(cur_alpha > 0)[0])
        ### I will be doing more work but its fine.  I will be visiting more edges which zero probability.
        for i_1 in pre_indexes:
            for i_2 in cur_indexes:
                ep = eprons[i-1]
                jp = tuple(jprons[i_1:i_2])
                prob = (alpha[i-1][i_1] * prior[ep][jp] * beta[i][i_2]) /alpha[numE][numJ]
                if prob > 0:
                    eplison[i][ep][jp] = prob


    return eplison






    #
    #
    # for a in EnumAligns(eprons, jprons, []):
    #     e, j = 0, 0
    #     p_x_z = 1.
    #     for (ep, js) in a:
    #         e += 1
    #         j += len(js)
    #         #p(x | z) : whole word alignment prob
    #         p_x_z *= alpha[e][j] * beta[e][j] * prior[ep][js]
    #
    #         counts[ep][js] += 1
    #
    # # now we need to do something with p_x_z
    #
    #
    # # normalize...?
    # for e, d in counts.items():
    #     for j in d.keys():
    #         counts[e][j] /= beta[1][1]





def Maximization(wordPairs, fracCount, prior):
    updated_prior = defaultdict(lambda :defaultdict(float))
    sum_prob = defaultdict(float)

    for i in range(len(wordPairs)):
        for t in fracCount[i]:
            for key in fracCount[i][t]:
                for key1 in fracCount[i][t][key]:
                    updated_prior[key][key1] += fracCount[i][t][key][key1]
                    sum_prob[key]+=fracCount[i][t][key][key1]

    for key in updated_prior:
        for key1 in updated_prior[key]:
            updated_prior[key][key1] =  updated_prior[key][key1]/sum_prob[key]


    return updated_prior









# def Maximization(wordPairs, counts, prior, maxE2J):
#     # recompute probabilities based on new "data"
#     for eword, jword in wordPairs:
#         eword, jword = eword.split(), jword.split()
#         for ephon in eword:
#             for j in range(len(jword)):
#                 for k in range(1, min(len(jword) - j, maxE2J) + 1):
#                     js = tuple(jword[j : j + k])
#                     # prob = ??



'''
forward
eprons:     list of English sounds
jprons:     list of Japanese sounds
prior:      dict mapping e->j->p where p is current prob. est.
maxE2J:     maximum k in k-to-1 mapping
'''
def Forward(eprons, jprons, prior, maxE2J):
    # alpha: prob. of getting to this state by some path from start
    numJ, numE = len(jprons), len(eprons)
    alpha = [[0. for i in range(numJ + 1)] for j in range(numE + 1)]
    alpha[0][0] = 1.
    # find alpha for each alignment
    for i in range(numE):
        for j in range(numJ):
            for k in range(1, min(numJ - j, maxE2J) + 1):
                ep, js = eprons[i], tuple(jprons[j : j + k])
                alpha[i + 1][j + k] += alpha[i][j] * prior[ep][js]

    return alpha
    #return [row[1 :] for row in alpha[1 :]]



'''
backward
eprons:     list of English sounds
jprons:     list of Japanese sounds
prior:      dict mapping e->j->p where p is current prob. est.
maxE2J:     maximum k in k-to-1 mappings
'''
def Backward(eprons, jprons, prior, maxE2J):
    # beta: prob. of getting to final state from this state
    numJ, numE = len(jprons), len(eprons)
    beta = [[0. for i in range(numJ + 1)] for j in range(numE + 1)]
    beta[numE][numJ] = 1.
    for i in range(numE - 1, -1, -1):
        for j in range(numJ - 1, -1, -1):
            for k in range(min(j, maxE2J) + 1):
                ep, js = eprons[i], tuple(jprons[j - k : j + 1])
                beta[i][j - k] += beta[i + 1][j + 1] * prior[ep][js]

    # for row in beta:
    #     row.insert(0, 0)
    # beta.insert(0, [0 for x in beta[-1]])
    return beta
    #return [row[: numJ] for row in beta[: numE]]






'''
ReadEpronJpron
get word pairs from file
'''
def ReadEpronJpron(filename):
    wordPairs = []
    with open(filename) as fp:
        for i, line in enumerate(fp.readlines()):
            if i % 3 == 0:
                eword = line.strip('\n')
            elif i % 3 == 1:
                jword = line.strip('\n')
                wordPairs.append((eword, jword))

    return wordPairs



'''
EnumAligns
enumerate all possible alignments
ephon:  list of English phonemes
jphon:  list of Japanese phonemes
'''
def EnumAligns(ephon, jphon, pre = []):
    aligns = []
    ep = ephon[0]
    for i in range(1, min(3, len(jphon)) + 1):
        js = tuple(jphon[: i])
        if len(ephon) == 1 and len(jphon) - i == 0:
            aligns.append(pre + [(ep, js)])
        elif len(ephon) == 1 or len(jphon) - i == 0:
            continue
        else:
            s = [(ep, js)]
            post = EnumAligns(ephon[1 :], jphon[i :], s)
            for p in post:
                aligns.append(pre + p)

    return aligns



'''
InitProb
initialize probabilities of possible alignments
'''
def InitProb(pairs):
    counts = defaultdict(lambda: defaultdict(int))
    for ew, jw in pairs:
        ew, jw = ew.split(), jw.split()
        aligns = EnumAligns(ew, jw, [])
        for alt in aligns:
            for (ep, js) in alt:
                counts[ep][js] += 1

    # initialize probabilities from "observed" counts
    probs = defaultdict(lambda : defaultdict(float))
    for ep, js_co in counts.items():
        n = sum(js_co.values())
        for js, co in js_co.items():
            probs[ep][js] = float(co) / n

    return probs




if __name__ == '__main__':
    fname = 'data/epron-jpron.data'
    pairs = ReadEpronJpron(fname)
    #pairs = [('W AY N','W A I N')]
    prior = InitProb(pairs)


    iters = 2

    Uprior = prior
    for i in range(iters):

        prior = Uprior
        print('iteration ', i, ' ----- ')
        #########
        count = 0
        for key in prior:
            print(key, '|->', end=' ')
            for key1 in prior[key]:
                if prior[key][key1] > 0.001:
                    count += 1
                    print(' '.join(key1), ':', round(prior[key][key1], 3), end=' ')
            print('\n')
        print('nonzeros =', count)
        ##########

        counts = Expectation(pairs, prior, 3)
        Uprior = Maximization(pairs, counts, prior)
