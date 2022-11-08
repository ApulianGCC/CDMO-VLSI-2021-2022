param w;
param n;
param min_h;
param max_h;
set BLOCKS;
param width {BLOCKS} integer;
param height {BLOCKS} integer;

var X {i in BLOCKS} integer >= 0, <= w - min(width[i]);
var Y {j in BLOCKS} integer >= 0, <= max_h - min(height[j]);
var h integer >= min_h, <= max_h;

var Z1 {1..n,1..n} binary;
var Z2 {1..n,1..n} binary;
var Z3 {1..n,1..n} binary;
var Z4 {1..n,1..n} binary;

subj to PositiveX {a in BLOCKS} : X[a] >= 0;
subj to PositiveY {a in BLOCKS} : Y[a] >= 0;
subj to BoundX {a in BLOCKS} : X[a] + width[a] <= w;
subj to BoundY {a in BLOCKS} : Y[a] + height[a] <= h;

#Non Overlapping
subj to ALeftB {a in BLOCKS, b in BLOCKS} : if a<b then X[a] + width[a] <= X[b] + w*(1 - Z1[a,b]);
subj to BLeftA {a in BLOCKS, b in BLOCKS} : if a<b then X[b] + width[b] <= X[a] + w*(1 - Z2[a,b]);
subj to AAboveB {a in BLOCKS, b in BLOCKS} : if a<b then Y[a] + height[a] <= Y[b] + max_h*(1 - Z3[a,b]);
subj to BAboveA {a in BLOCKS, b in BLOCKS} : if a<b then Y[b] + height[b] <= Y[a] + max_h*(1 - Z4[a,b]);

subj to LeftOrRight {a in BLOCKS, b in BLOCKS} : if a<b then 1 >= Z1[a,b] + Z2[a,b];
subj to AboveOrBelow {a in BLOCKS, b in BLOCKS} : if a<b then 1 >= Z3[a,b] + Z4[a,b];
#A constraint programming approach for the two-dimensional rectangular packing problem with orthogonal orientations
subj to AtLeastOne {a in BLOCKS, b in BLOCKS} : if a<b then 1 <= Z1[a,b] + Z2[a,b] + Z3[a,b] + Z4[a,b];

#Symmetry Breaking
subj to FirstPairConstraint :  (X[1] + (width[1] div 2) + Y[1] + (height[1] div 2)) <= (X[2] + (width[2] div 2) + Y[2] + (height[2] div 2));
subj to FixedBiggestBlockX : (X[1] + (width[1] div 2)) <= w div 2;
subj to FixedBiggestBlockY : (Y[1] + (height[1] div 2)) <= (max_h + min_h) div 4;

minimize tmpH : h;