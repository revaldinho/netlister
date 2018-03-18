//
// comments can be added as usual in verilog format
//
module myboard ();

   // wire declarations
//   wire   a, b;
   wire   c;
   wire   complicated_name_102, f, h;
   supply0 VSS;
   supply1 VDD;

   wire    c;
   wire    declared_but_not_used;
      
   wire    k,m;
   
   
   // component section - has some intentional errors and undeclared wires
   INV U0 ();
   
   INV U1 ( .i(a), .o(b), .o(j) );
   INV U1 ( .i(a), .o(b), .o(f) );   
   INV U2 ( .i(b), .o() );
   NAND U4 ( .i0(b), .i1(c), .o() );
   BUF U5 ( .i(VSS), .o(f) );
   BUF U6 ( .i(f), .o(c) );
   BUF U19 ( .i(VDD), .o(k) );   
// example dud component
//   BUT U8 ( .i(f), .o(c) );   
   NOR U9 ( .i0(f), .i1( complicated_name_102), .o(h) );         
   SPACER U3 ();
   AOI U7 ( .i0(a),
            .i1(b),
            .i2(c),
            .o(f) );
   AOI U10 ( .i0(),
            .o(m) );   
   
endmodule
