#!/usr/bin/env python 
#
# Quick hack to compare two Eagle netlists
#
# Usage: netcompare.py file1.net file2.net
#
# Eagle seems case insensitive so all nets/components are converted to uppercase before comparison
#
# requires python 2.4 or greater
#
# 
import sys, getopt
def read_eagle_file ( filename ) :
    f = open ( filename, "r" )
    netlist = dict ()
    start = False
    connection_list = dict()
    key = "null"
    for l in f.readlines():
        words = ( l.upper()).split();
        if not start :
            if len(words) > 0 and words[0] == "NET" :
                start = True
                connection_list = dict()
        else:
            # Blank line marks end of last
            if len(words) == 0 :
                if key != "null" and connection_list:                    
                    netlist[key] = connection_list
                connection_list = dict()
            else :
                if not connection_list :
                    key = words[0]
                    words = words[1:]
                for i in xrange ( 0, len(words), 2 ) :                    
                    if words[i] in connection_list :
                        connection_list[words[i]].append( words[i+1])
                    else:
                        connection_list[words[i]] = [words[i+1]]
    # Make sure we get the last entry even if the
    # file doesn't end with a newline
    if len(connection_list) > 0 :
        netlist[key] = connection_list
    return netlist

def compare_netlists ( net1, net2 ) :
    # Decidedly non-optimal comparison of the two netlists
    match = True
    for k in net1.iterkeys() :
        # Check all nets in netlist1 are found in netlist2
        if not k in net2 :
            match = False
            print "Net %s in file1 but not in file2" % k
        else : 
            # For nets in both netlists check first
            # that the components the nets are connected to
            # are identical and then, that the nets connect
            # to the same pins on those components
            n1_components =  sorted(net1[k].keys())
            n2_components =  sorted(net2[k].keys())
            for c in n1_components:
                if c not in n2_components:
                    match = False
                    print "Fail on net %s : has connection to component %s in file1 but not in file2" %( k,c)
                else:
                    if sorted((net1[k])[c]) != sorted((net2[k])[c]):
                        match = False
                        print "Mismatch on connections for component", c
                        print "file1:", (net1[k])[c]
                        print "file2:", (net2[k])[c]
                        
            for c in n2_components:
                if c not in n1_components:
                    match = False
                    print "Fail on net %s : has connection to component %s in file2 but not in file1" %( k,c)
                    

    for k in net2.iterkeys() :
        # Check all nets in netlist2 are found in netlist1
        if not k in net1 :
            match = False
            print "Net %s in file2 but not in file1" % k
            
    if match : 
        print "PASS - netlists match"
    else :
        print "FAIL - netlists don't match"


if __name__ == "__main__" :
    if len(sys.argv) < 3 :
        print "Usage: netcmp.py file1 file2"
        sys.exit()
                
    net1 = read_eagle_file( sys.argv[1] )
    net2 = read_eagle_file( sys.argv[2] )

    compare_netlists( net1, net2 ) 
