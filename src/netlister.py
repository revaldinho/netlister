#!/usr/bin/env jython
"""
Netlister tool to convert and check between Verilog-like HDL and Eagle netlists
"""

from vnx import parser
import getopt, re, sys

# Global Variables
g_lib_comp_list = []
g_comp_lib_dict = {}
g_net_fanout_table = dict()
g_warnings = dict()
g_fanout_check=False

def module_declaration(p):
    """
    Read the top level module definition and return the module name
    """
    p.eat("module")
    board_name = (p.getIdent()).encode()
    p.eat("(")
    p.eat(")")
    p.eat(";")
    return board_name


def warning( type, message ) :
    global g_warnings

    print "warning (%s): %s" % (type, message )
    if type not in g_warnings:
        g_warnings.update( { type:1 } )
    else:
        g_warnings.update( { type: (g_warnings[type]+1) } )

def error ( message ) :
    print message
    sys.exit(1)


def wire_declaration(p):
    """
    Read a complete wire declaration clause and return the list of names
    """
    passed_eol = p.advance()
    wirelist = []
    while p.token != u";" :
        s = p.getIdent()
        if p.token == u",":
            p.advance()
        wirelist.append( s.encode())
    p.eat(";")
    return wirelist

def component_instance( nets, p):
    """
    Read a component instance from source and return the component data
    """
    component_type = (p.getIdent()).encode()
    instance_name = (p.getIdent()).encode()
    pin_mapping = dict()

    pins_used = []
    p.eat("(")
    if p.token == u".":
        while p.token != u")":
            wire_name = ""
            p.advance()
            pin_name = (p.getIdent()).encode()
            if pin_name in pins_used :
                warning( "PIN-1", "pin %s of component %s appears more than once in component instance %s on line %s" % \
                    (pin_name,component_type, instance_name, str(p.st.lineno())))

            else :
                pins_used.append(pin_name)
            p.eat("(")
            if p.token != u")" :
                wire_name = (p.getIdent()).encode()
                if wire_name not in nets :
                    warning( "NET-1", "use of undeclared wire %s on line %s, adding wire to netlist" % \
                    (wire_name,  str(p.st.lineno())))
                    nets.append( wire_name )
            p.eat(")")
            if p.token == u",":
                p.advance()
            if not wire_name == "" :
                pin_mapping.update( {pin_name:wire_name} )
        p.eat(")")
    else:
        p.eat(")")
    p.eat(";")
    return (component_type, instance_name, pin_mapping)


def create_net_fanout_table( components ):
    """
    Read the current component oriented netlist and create a net
    oriented version instead.
    """
    net_fanout_table = dict()
    for (name, inst, mapping) in components:
        for pin in mapping.iterkeys():
            net = mapping[pin]
            if net in net_fanout_table:
                l = net_fanout_table[net]
                l.append( (name, inst, pin))
            else:
                net_fanout_table.update( {net:[(name, inst, pin)]} )
    return net_fanout_table

def create_eagle_netlist( board_name, components, libs ) :
    """
    Convert to net-oriented list ready for writing out in Eagle format
    """
    outputlines = []

    # Print out net data in Eagle-like format
    outputlines.append( "Netlist "+board_name + "\n")
    outputlines.append( "Exported from netlister $Revision$\n")
    outputlines.append( "EAGLE\n")
    outputlines.append( "%-20s  %-20s  %-20s\n" % ( "Net", "Part", "Pad"))

    # Better - but not available in Jython2.2
    # for net in sorted(g_net_fanout_table.iterkeys()) :
    for net in g_net_fanout_table.iterkeys() :
        net_name = net
        for (comp, inst, pin) in g_net_fanout_table[net_name] :
            # Map the pin to the Eagle library element
            (lib_name, eagle_lib, eagle_comp, pin_mapping) = g_comp_lib_dict[comp]
            if ( pin in pin_mapping ) :
                outputlines.append( "%-20s  %-20s  %-20s" % ( net_name, inst, pin_mapping[pin]))
            else:
                print "ERROR : cannot find pin name %s in mapping for %s" % (pin,comp)
            net_name = ""
        outputlines.append("")
    return '\n'.join(outputlines)

def create_eagle_scr( board_name, components, libs, supply_nets ) :
    """
    Convert to Eagle script output
    """
    outputlines = []

    outputlines.append( "# Netlist "+board_name + "\n")
    outputlines.append( "# Exported from netlister $Revision$")
    outputlines.append("Layer Top;")
    # Set default to inches for component creation and pre-placement
    outputlines.append("Grid Inch;")
    #
    #Print out the components and place offset to the origin
    libraries_used = []
    component_data = []
    for  (name, inst, mapping) in components:
        (lib_name, eagle_lib, eagle_comp, pin_mapping) = g_comp_lib_dict[name]
        if eagle_lib not in libraries_used:
            libraries_used.append( eagle_lib)
        component_data.append( "ADD %s@%s %s R0 (1.5 1.5); # %s" %
                               (eagle_comp ,eagle_lib,inst, name))

    outputlines.append("\n# Libraries")
    for l in libraries_used:
        outputlines.append("USE %s ;" % l )

    outputlines.append("\n# Component Instances")
    outputlines.extend(component_data)

    outputlines.append("\n# Define net classes")
    outputlines.append("CLASS 0 default ;")
    outputlines.append("CLASS 1 supply ;")

    outputlines.append("\n# Define net connections")
    outputlines.append("change class 0  ;")
    current_class = 0

    # Better - but not available in Jython2.2
    #for net in sorted(g_net_fanout_table.iterkeys()) :
    for net in g_net_fanout_table.iterkeys() :
        if (net in supply_nets) and (current_class == 0):
            outputlines.append("\nchange class 1  ;")
            current_class = 1
        elif (net not in supply_nets) and (current_class == 1) :
            outputlines.append("\nchange class 0  ;")
            current_class = 0
        signal_list = ["SIGNAL "+net]
        for (comp, inst, pin) in g_net_fanout_table[net] :
            # Map the pin to the Eagle library element
            (lib_name, eagle_lib, eagle_name, pin_mapping) = g_comp_lib_dict[comp]
            if ( pin in pin_mapping ) :
                signal_list.append( inst + " " + str( pin_mapping[pin]) )
            else:
                print "ERROR : cannot find pin name %s in mapping for %s" % (pin,comp)
        outputlines.append( ' '.join(signal_list) + ';')

    # Write out some defaults for Polygon handling
    outputlines.append("change Thermals On ;")
    outputlines.append("change Isolate 0.015 ;")
    outputlines.append("change Orphans Off ;")

    return '\n'.join(outputlines) + '\n'


def read_library( filename ):
    """
    Eval a library file directly into a python data structure
    """
    libelements = eval(file(filename).read())
    # Do some rudimentary checking on the contents
    (name, components) = libelements

    legal_vlog_name = re.compile("[a-zA-Z]([a-zA-Z0-9_]*)")
    for module_name in components:
        if not legal_vlog_name.match(module_name):
            warning("LIB-1","Library %s has illegal module name %s" %(name, module_name))

        (package, eagle_lib, mapping) = components[module_name]
        port_names = mapping.keys()
        for i in xrange(0, len(port_names)):
            for j in xrange( i+1, len(port_names)):
                if mapping[port_names[i]] == mapping[port_names[j]]:
                    warning("LIB-2","Library definition for module %s maps both %s and %s to the same package pin %s" % ( module_name, port_names[i], port_names[j], str(mapping[port_names[j]])))


    return libelements


def link_netlist( components, nets, libs ):
    """
    Check netlist vs the libraries and create a number of mapping structures.

    Return false in case of errors (or maybe just bail out if they're fatal).
    """
    global g_lib_comp_list
    global g_comp_lib_dict
    global g_net_fanout_table

    # Extract the components available from the libraries into a flat list
    for (lib_name, lib_mapping) in libs:
        g_lib_comp_list.extend(lib_mapping.keys())

    # Check that all components in the netlist are found in a library and make
    # a hash to store the relation and include the pin mapping so both can
    # be looked up using the component name as a key
    for (comp, inst, mapping) in components:
        found = False
        for (lib_name, lib_mapping) in libs:
            if comp in lib_mapping:
                (name, eagle_lib, pin_mapping) = lib_mapping[comp]
                g_comp_lib_dict.update( {comp:(lib_name, eagle_lib, name, pin_mapping)} )
                found = True
                break
        if not found:
            error("ERROR : cannot find component in available libraries: "+comp)

    g_net_fanout_table = create_net_fanout_table( components )

    # Some brief checking on the completed data structures:
    # 1. Find and report all unused nets and 1-pin nets
    # 2. Find and report unconnected pins on all instances

    for n in nets:
        if not n in g_net_fanout_table:
            warning ("NET-2", "warning: net %s is declared but not used" % n )
        elif len(g_net_fanout_table[n]) == 1 :
            warning ("NET-3", "warning: net %s is connected to only one pin in the netlist" % n)

    for (comp, inst, mapping) in components:
        # Get the pin out data from the library file and check that all pins specified
        # for that cell have been assigned to the pin mapping of the cell instance
        (libname, eaglelib_name, name, ref_pin_mapping) = g_comp_lib_dict[comp]
        for p in ref_pin_mapping:
            if p not in mapping :
                warning( "INST-2", "pin %s of component instance %s (type %s) is not connected" % (p, inst, comp))


    # additional checks
    if g_fanout_check:
        print ("Net Fanout Table\n")
        line = []
        for i in range (0,4):
            line.append("%-16s :  #" % "Net Name")
        print(' |'.join(line))
        line = []
        for i in range (0,4):
            line.append("%-16s------" % ( 16*'-'))
        print('|'.join(line))
        i=0
        line = []
        for n in sorted(nets):
            if n in g_net_fanout_table :
                line.append("%-16s :%3d" % ( n, len(g_net_fanout_table[n])))
            else:
                line.append("%-16s :%3d" % ( n, 0))
            i+=1
            if i % 4==0 :
                print (' |'.join(line))
                line = []


def usage():
    usage_string = """

  USAGE:

    The netlists.py program converts verilog-like netlists into a format
    suitable for reading into the Eagle PCB creation tool.

  REQUIRED SWITCHES

    -i  --inputfile  <filename>   specify the input netlist file
    -f  --format     <net|scr>    specify the output file format
    -l  --library    <filename>   specify at least one library file

    If multiple libraries are required, then these can either be entered by
    using multiple -l <filename> pairs, or by quoting all the library filenames
    into a colon separated string.

  OPTIONAL SWITCHES

    -o  --outputfile <filename>   specify the output file (default is to
                                  write to stdout)

    -d  --header    <filename>    specify a file of text which will be prepended
                                  to the output file. Use this for copyright
                                  messages or other boilerplate text as required.
    -t  --footer    <filename>    specify a file of text which will be appended
                                  to the output file. Usually this is used with
                                  SCR output to add component placement or other
                                  Eagle board commands which can't be expressed
                                  in the source netlist.
    -u  --fanout                  write a net fanout table to help check net
                                  connections
    -h  --help                    print this usage message.

  EXAMPLES

    jython netlister.py -i myboard.v -o myboard.scr -f scr -l mylib.lib
    """
    print usage_string
    sys.exit(0)


def main( argv ):
    """
    Command line option parsing.
    """
    global g_fanout_check


    infile = ""
    outfile = ""
    format = "scr"
    header = ""
    footer = ""
    libfiles = []

    try:
        opts, args = getopt.getopt( argv[1:], "i:o:f:l:d:t:hu", [
                "inputfile=", "outputfile=", "format=", "library=", "header=",
                "footer=", "help", "fanout"])
    except getopt.GetoptError, err:
        print str(err)
        usage()

    for opt, arg in opts:
        if opt in ( "-i", "--inputfile" ) :
            infile = arg
        elif opt in ( "-o", "--outputfile" ) :
            outfile = arg
        elif opt in ( "-f", "--format" ) :
            format = arg.lower()
        elif opt in ( "-l", "--lib", "--library") :
            if ':' in arg:
                libfiles.extend( arg.split(':') )
            else :
                libfiles.append( arg )
        elif opt in ( "-d", "--header" ) :
            header = arg
        elif opt in ( "-t", "--footer" ) :
            footer = arg
        elif opt in ("-h", "--help" ) :
            usage()
        elif opt in ("-u", "--fanout" ) :
            g_fanout_check=True

    # Check that all mandatory arguments have been given
    if not ( infile and (format in ["scr","net"]) and libfiles ):
        usage()


    p = parser(infile)
    libs = []
    for l in libfiles:
        libs.append(read_library(l))

    nets = []
    supply_nets = []
    components = []
    instances = []

    # -- Main code to parse the entire netlist file
    p.advance()
    board_name = module_declaration(p)
    while p.token != u"endmodule" and p.token != u"(eof)":
        # See if it's a wire declaration
        if p.token == u"wire" or p.token.startswith(u"supply"):
            net_type = p.token
            for w in wire_declaration(p) :
                if not w in nets:
                    nets.append(w)
                    if net_type.startswith(u"supply"):
                        supply_nets.append(w)
                else:
                    warning( "NET-4","net %s declared more than once on line %s" % \
                    (w,  str(p.st.lineno())))
        else:
            # Assume it's a component
            ( type, inst, map) = component_instance(nets, p )
            if not inst in instances:
                components.append( ( type, inst, map) )
                instances.append( inst)
            else :
                warning( "INST-1","instance %s appears more than once in netlist on line %s" % \
                    (inst,  str(p.st.lineno())))

    p.eat("endmodule")
    # -- end of parsing code


    link_netlist(components, nets, libs)


    # Create and output an  netlist
    if outfile:
        f = file(outfile,"w")
    else:
        f = sys.stdout

    if header :
        f.write( file(header).read())
    if format == "net":
        f.write( create_eagle_netlist( board_name, components, libs))
    else :
        f.write( create_eagle_scr( board_name, components, libs, supply_nets))
    if footer :
        f.write( file(footer).read())

    # Move this to an optional proc.
    # print "Summary"
    # print "number of nets: %d" %len(nets)
    # print "number of instances: %d" % len(instances)

    if len (g_warnings) :
        print "Netlist translated with warnings in %d categories:" % len(g_warnings)
        warning_list = g_warnings.keys()
        warning_list.sort()
        for k in warning_list:
            print "%3d warnings of type %s" % ( g_warnings[k], k)
    else :
        print "Netlist translated with no warnings"

    f.close()


if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)
