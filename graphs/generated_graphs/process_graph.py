import sys
import json 

if __name__ == '__main__':
    
    augmented_edges = {u'85,t': 3, u'10,30': 1, u'40,t': 5, u'72,t': 6, u'91,t': 1, u'67,74': 2, u'62,t': 1, u's,t': 9, u'3,2': 1, u'64,93': 1, u's,45': 10, u's,46': 9, u's,41': 1, u's,40': 4, u's,43': 8, u's,42': 2, u'66,t': 1, u'51,t': 3, u'10,27': 1, u'19,t': 2, u'57,t': 1, u'53,1': 6, u'36,t': 1, u'48,88': 3, u'14,11': 3, u'38,t': 5, u'22,21': 3, u'58,t': 4, u's,9': 3, u'23,92': 1, u's,6': 5, u'11,t': 9, u's,3': 7, u's,31': 6, u's,33': 9, u'20,11': 2, u's,36': 1, u'65,25': 1, u's,38': 2, u's,39': 1, u'77,t': 5, u'71,t': 9, u'92,t': 1, u'10,19': 2, u'31,5': 2, u'74,55': 1, u'43,t': 6, u's,2': 4, u'74,59': 4, u'5,t': 3, u'46,15': 2, u'22,34': 2, u'24,t': 6, u'62,48': 5, u's,22': 9, u's,20': 10, u's,26': 6, u'62,95': 1, u's,28': 9, u'93,88': 1, u's,83': 5, u's,85': 3, u's,87': 2, u's,88': 3, u'3,51': 2, u'43,48': 2, u'22,12': 2, u'52,91': 1, u'12,t': 4, u'52,11': 1, u'0,34': 2, u'28,40': 1, u'22,42': 2, u'28,48': 1, u'41,34': 1, u'63,15': 2, u'63,17': 4, u's,14': 3, u'8,t': 9, u'15,42': 1, u's,10': 8, u's,11': 4, u'31,8': 3, u'42,t': 7, u'83,t': 5, u's,71': 9, u's,72': 6, u'25,81': 2, u'58,5': 1, u'27,t': 2, u'45,38': 2, u'87,t': 8, u'48,38': 1, u'28,55': 1, u'33,42': 2, u'59,t': 6, u'53,39': 2, u'48,t': 6, u'34,t': 8, u'30,t': 2, u'55,t': 9, u's,67': 2, u'20,24': 6, u's,65': 4, u's,64': 1, u'20,21': 2, u's,62': 7, u'10,12': 2, u'2,t': 9, u'31,35': 1, u'28,27': 1, u'28,21': 2, u'45,t': 8, u'1,87': 6, u'3,48': 3, u'28,t': 1, u'26,55': 3, u'69,t': 5, u's,52': 2, u's,53': 9, u'33,8': 6, u's,51': 1, u'46,0': 2, u'15,81': 3, u'17,55': 4, u'81,t': 5, u'6,58': 5, u'88,t': 7, u's,69': 5, u'53,23': 1, u'48,57': 1, u'39,34': 1, u'3,35': 1, u'28,30': 1, u's,66': 4, u'63,25': 1, u'95,34': 1, u'28,2': 1, u'33,t': 1, u'35,t': 2, u's,63': 7, u'65,t': 3, u'39,59': 2, u'26,2': 3, u'46,77': 5, u'9,t': 3, u'21,t': 7, u'66,74': 3, u'11,34': 1, u'10,t': 2}

    graph = open("generated_graph_100", "r")

    edges_to_t = {}
    aug_edges_to_t = {}

    for line in graph:
        split_line = line.split("\t")
        v, n = json.loads(split_line[0]), json.loads(split_line[1])
#        print "n " + str(n)
        for edge in n:
            print "edge " + str(edge)
            e_v, e_c = edge
            if e_v == "t":
                edges_to_t[v] = e_c

    for key in augmented_edges:
        src, sink = key.split(",")
        if sink == "t":
            aug_edges_to_t[src] = augmented_edges[key]

    keylist = edges_to_t.keys()
    keylist.sort()
    print "Printing edges to t" 
    for key in keylist:
        print str(key) + "\t" + str(edges_to_t[key]) + "\n"
    
    aug_keylist = int(aug_edges_to_t.keys())
    aug_keylist.sort()
    print "Printing aug edges to t"
    for key in aug_keylist:
        print str(key) + "\t" + str(aug_edges_to_t[key]) + "\n"

    
    
