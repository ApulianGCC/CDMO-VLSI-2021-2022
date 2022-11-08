param w;
param n;
param min_h;
param max_h;
set BLOCKS;
param width {BLOCKS} integer;
param height {BLOCKS} integer;

var X {i in BLOCKS} integer >= 0, <= w;
var Y {j in BLOCKS} integer >= 0, <= max_h;
var h integer >= min_h, <= max_h;

var Z1 {1..n,1..n} binary;
var Z2 {1..n,1..n} binary;
var Z3 {1..n,1..n} binary;
var Z4 {1..n,1..n} binary;

var R {1..n} binary;

subj to PositiveX {a in BLOCKS} : X[a] >= 0;
subj to PositiveY {a in BLOCKS} : Y[a] >= 0;
subj to BoundX {a in BLOCKS} : X[a] + (1-R[a])*(width[a]) + R[a]*height[a] <= w;
subj to BoundY {a in BLOCKS} : Y[a] + (1-R[a])*(height[a]) + R[a]*width[a] <= h;

#Non Overlapping
subj to ALeftB {a in BLOCKS, b in BLOCKS} : if a<b then X[a] + (1-R[a])*(width[a]) + R[a]*height[a] <=  X[b] + w*(1-Z1[a,b]);
subj to BLeftA {a in BLOCKS, b in BLOCKS} : if a<b then X[b] + (1-R[b])*(width[b]) + R[b]*height[b] <= X[a] + w*(1 - Z2[a,b]);
subj to AAboveB {a in BLOCKS, b in BLOCKS} : if a<b then Y[a] + (1-R[a])*(height[a]) + R[a]*width[a] <= Y[b] + max_h*(1 - Z3[a,b]);
subj to BAboveA {a in BLOCKS, b in BLOCKS} : if a<b then Y[b] + (1-R[b])*(height[b]) + R[b]*width[b] <= Y[a] + max_h*(1 - Z4[a,b]);

#A constraint programming approach for the two-dimensional rectangular packing problem with orthogonal orientations
subj to LeftOrRight {a in BLOCKS, b in BLOCKS} : if a<b then 1 >= Z1[a,b] + Z2[a,b];
subj to AboveOrBelow {a in BLOCKS, b in BLOCKS} : if a<b then 1 >= Z3[a,b] + Z4[a,b];
subj to AtLeastOne {a in BLOCKS, b in BLOCKS} : if a<b then 1 <= Z1[a,b] + Z2[a,b] + Z3[a,b] + Z4[a,b];

#Symmetry Breaking
#subj to FirstPairConstraintX: X[1] <= X[2];
#subj to FirstPairConstraintY: Y[1] <= Y[2];
#subj to FixedBiggestBlockX: X[1] <= w div 2;
#subj to FixedBiggestBlockY: Y[1] <= (max_h + min_h) div 4;

minimize tmpH : h;