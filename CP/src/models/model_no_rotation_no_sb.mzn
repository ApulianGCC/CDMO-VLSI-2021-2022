include "globals.mzn";

% Params
int: w;
int: n;
array [1..n,1..2] of int: circuits_shape;

% I save all the widths and heights of the blocks, ordered decreasingly by the area. 
array[1..n] of int: indexes = arg_sort([-circuits_shape[i,1] * circuits_shape[i,2] | i in 1..n]);
array[1..n] of int: widths = [circuits_shape[i, 1] | i in indexes];
array[1..n] of int: heights = [circuits_shape[i, 2] | i in indexes]; 

array[1..n] of int: areas = [circuits_shape[i, 1] * circuits_shape[i, 2] | i in 1..n];

%Bounds for the minimum and maximum height
array[int] of int: index_new_row = [1] ++ 
[i | i in 2..n  where (sum([widths[j] | j in 1..i])-1) mod w < (sum([widths[j] | j in 1..i-1])-1) mod w]  ++ [n];  
               
int: max_h = sum([max([heights[j] | j in index_new_row[i-1]..index_new_row[i]]) | i in 2..length(index_new_row)]);
int: min_h = max(ceil(sum(areas)/ w), max(heights));


% Height we want to minimize
var min_h..max_h:  h;

% Arrays containing the coordinates of the bottom-left corner of each block
array[1..n] of var 0..w - min(widths) : x;
array[1..n] of var 0..max_h - min(heights): y;


% Placement constraints
constraint forall(i in 1..n) (x[i] + widths[i] <= w /\ y[i] + heights[i] <= h) ::bounds;

%No overlapping global constraint
constraint diffn(x,y,widths,heights);

% Usage of the space global constraints
constraint cumulative(x, widths, heights, h) ::domain;
constraint cumulative(y, heights, widths, w) ::domain;

ann: search_annotation = seq_search([
							int_search(x, first_fail, indomain_min), 
							int_search([h], input_order,indomain_median),
							int_search(y, smallest, indomain_min),
          		
]) :: restart_luby(60) ::relax_and_reconstruct(y,50);

solve :: search_annotation minimize h;

output[show(w) ++
			" " ++
			show(h) ++
			"\n" ++
			show(n) ++
			"\n" ++
			show(widths) ++
			"\n" ++
			show(heights) ++
			"\n" ++
			show(x) ++ 
			"\n" ++
			show(y)
];