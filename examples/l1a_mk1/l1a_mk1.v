//
// level1a board
//

module l1a_mk1();

   supply0 VSS;
   supply1 VDD;

   wire    cpu_d0, cpu_d1, cpu_d2, cpu_d3, cpu_d4, cpu_d5, cpu_d6, cpu_d7;
   wire    bbc_d0, bbc_d1, bbc_d2, bbc_d3, bbc_d4, bbc_d5, bbc_d6, bbc_d7;   
   wire    a0, a1, a2, a3, a4, a5, a6, a7, a8, a9,
           a10, a11, a12, a13, a14, a15;
   wire    vpa, vda, vpb, e, rdnw, rstb, irqb, nmib;
   wire    bbc_a15, bbc_rdnw;
   wire    cpu_a16, cpu_a17;   
   wire    ram_ceb;
   wire    rdy;   
   wire    phi0, phi1, bbc_ck8, cpu_ck_phi2;
   wire    ck8_1_n, ck8_2, ck8_3_n, ck8_4, ck8_5_n, bbc_ck8_del;
   wire    tdo, tdi, tck, tms;
   
   
   // decoupling caps
     cap100nf cap100nf_1 (
                  .p0( VSS ),
                  .p1( VDD )
                  );
     cap100nf cap100nf_2 (
                  .p0( VSS ),
                  .p1( VDD )
                  );
     cap100nf cap100nf_3 (
                  .p0( VSS ),
                  .p1( VDD )
                  );
     cap100nf cap100nf_4 (
                  .p0( VSS ),
                  .p1( VDD )
                  );

   

   
   wdc65816 IC1 (
            .vpb(vpb),
            .rdy(rdy),
            .abortb(VDD),
            .irqb(irqb),
            .mlb(),
            .nmib(nmib),
            .vpa(vpa),
            .vcc(VDD),
            .a0(a0),
            .a1(a1),
            .a2(a2),
            .a3(a3),
            .a4(a4),
            .a5(a5),
            .a6(a6),
            .a7(a7),
            .a8(a8),
            .a9(a9),                        
            .a10(a10),                        
            .a11(a11),
            .vss2(VSS),
            .a12(a12),
            .a13(a13),
            .a14(a14),
            .a15(a15),
            .d7(cpu_d7),
            .d6(cpu_d6),
            .d5(cpu_d5),
            .d4(cpu_d4),
            .d3(cpu_d3),
            .d2(cpu_d2),
            .d1(cpu_d1),
            .d0(cpu_d0),
            .rdnw(rdnw),
            .e(e),
            .be(VDD),
            .phi2in(cpu_ck_phi2),
            .mx(),
            .vda(vda),
            .rstb(rstb)
            );
   


      bs62lv1027 IC2 (
            .a0(a0),
            .a1(a1),
            .a2(a2),
            .a3(a3),
            .a4(a4),
            .a5(a5),
            .a6(a6),
            .a7(a7),
            .a8(a12), // Use Eds trick of swapping addr bits to line up with CPU
            .a9(a14),                        
            .a10(cpu_a16),                        
            .a11(a15),
            .a12(a8),
            .a13(a13),
            .a14(a9),
            .a15(a11),
            .a16(a10),
            .d7(cpu_d7),
            .d6(cpu_d6),
            .d5(cpu_d5),
            .d4(cpu_d4),
            .d3(cpu_d3),
            .d2(cpu_d2),
            .d1(cpu_d1),
            .d0(cpu_d0),
            .nc1(cpu_a17), // connect up to allow use of 512KB RAM
            .vss(VSS),
            .vdd(VDD),
            .ceb(ram_ceb),
            .ce2(VDD),
            .web(rdnw),
            .oeb(ram_ceb)
            );



   L1A_9572 IC3 (
		 .cpu_clk_phi2(cpu_ck_phi2),
		 .cpu_vpb(vpb),
		 .cpu_vpa(vpa),      
		 .cpu_vda(vda),
		 .bbc_ck8(bbc_ck8_del),                 
		 .bbc_ck2_phi0(phi0),
		 .ram_addr16(cpu_a16),
		 .ram_addr17(cpu_a17),                 
		 .ram_ceb(ram_ceb),
		 .rdy(rdy),
		 .spare1(),
		 .bbc_ck2_phi1(phi1),
		 .bbc_rdnw(bbc_rdnw),
		 .bbc_addr15(bbc_a15),
		 .bbc_data0(bbc_d0),
		 .bbc_data1(bbc_d1),
		 .bbc_data2(bbc_d2),
		 .bbc_data3(bbc_d3),
		 .bbc_data4(bbc_d4),
		 .bbc_data5(bbc_d5),
		 .bbc_data6(bbc_d6),
		 .bbc_data7(bbc_d7),                 
		 .cpu_data0(cpu_d0),
		 .cpu_data1(cpu_d1),
		 .cpu_data2(cpu_d2),
		 .cpu_data3(cpu_d3),
		 .cpu_data4(cpu_d4),
		 .cpu_data5(cpu_d5),
		 .cpu_data6(cpu_d6),
		 .rstb(rstb),
		 .cpu_data7(cpu_d7),
		 .cpu_addr15(a15),
		 .cpu_rdnw(rdnw),
		 .cpu_e(e),
                 
                 
                 // JTAG - not used so connect to ground which lets us power up inner ring
                 .tck(tck),
                 .tms(tms),
                 .tdi(tdi),
                 .tdo(tdo),
                 // Supplies
                 // this is a func pin sacrificed to allow wide power routing to the inner circle
                 .auxgnd1(VSS), 
                 .gnd1(VSS),
                 .gnd2(VSS),
                 .gnd3(VSS),
                 .vccint1(VDD),
                 .vccint2(VDD),
                 .vccio(VDD)
                 
                 );
   
   SN7414  IC4 (
          .i0(bbc_ck8),
          .o0(ck8_1_n),
          .i1(ck8_1_n),
          .o1(ck8_2),
          .i2(ck8_2),
          .o2(ck8_3_n),
          .i3(ck8_3_n),
          .o3(ck8_4),
          .i4(ck8_4),
          .o4(ck8_5_n),
          .i5(ck8_5_n),
          .o5(),          
          .vss(VSS),
          .vdd(VDD)
          );
   
   DIP6  IC5 (
              .sw0_a(bbc_ck8),
              .sw0_b(bbc_ck8_del),
              .sw1_a(ck8_1_n),
              .sw1_b(bbc_ck8_del),
              .sw2_a(ck8_2),
              .sw2_b(bbc_ck8_del),
              .sw3_a(ck8_3_n),
              .sw3_b(bbc_ck8_del),
              .sw4_a(ck8_4),
              .sw4_b(bbc_ck8_del),
              .sw5_a(ck8_5_n),
              .sw5_b(bbc_ck8_del)
              );
   

   
   skt6502_40w CON1 (
            .vss(VSS),
            .rdy(),
            .phi1out(phi1),
            .irqb(irqb),
            .nc1(),
            .nmib(nmib),
            .sync(),
            .vcc(VDD),
            .a0(a0),
            .a1(a1),
            .a2(a2),
            .a3(a3),
            .a4(a4),
            .a5(a5),
            .a6(a6),
            .a7(a7),
            .a8(a8),
            .a9(a9),                        
            .a10(a10),                        
            .a11(a11),
            .vss2(VSS),
            .a12(a12),
            .a13(a13),
            .a14(a14),
            .a15(bbc_a15),
            .d7(bbc_d7),
            .d6(bbc_d6),
            .d5(bbc_d5),
            .d4(bbc_d4),
            .d3(bbc_d3),
            .d2(bbc_d2),
            .d1(bbc_d1),
            .d0(bbc_d0),
            .rdnw(bbc_rdnw),
            .nc2(),
            .nc3(),
            .phi0in(phi0),
            .so(),
            .phi2out(),
            .rstb(rstb)
            );

   pcbheader2  con2 (
              .clkin(bbc_ck8)
              );

   // jtag header for in system programming
   hdr8way jtaghdr (
          .p1(VSS),  .p2(VSS),
          .p3(tms),  .p4(tdi),
          .p5(tdo),  .p6(tck),
          .p7(VDD),  .p8(),
          );

   // Power header is convenient if we allow in system programming
   powerheader3 pwrhdr(
                     .vdd1(VDD),
                     .vdd2(VDD),
                     .gnd(VSS)
                     );
   

   
endmodule
