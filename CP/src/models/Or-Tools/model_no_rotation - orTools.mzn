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

% Symmetry breaking constraints

% If two blocks have the same dimensions, then the first one has to be closer to the origin ( coordinates (0,0) ).
constraint forall(i,j in 1..n where i<j)(
		if widths[i] == widths[j] /\ heights[i] == heights[j] then
			(x[i] + y[i]) div 2 < (x[j] + y[j]) div 2 
		endif
);


% The block with the largest area is placed on the bottom-left area of the plate
constraint (x[1] < w div 2 /\ y[1] < h div 2); 

% I impose a given order for the first pair of elements.
constraint ((x[1] + y[1]) < (x[2] + y[2]) );


% Ordering for blocks with the same position on the y-axis and heieght
constraint (forall (i,j in 1..n where i<j) (
	if y[i] == y[j] /\ heights[i] == heights[j]  then x[i] < x[j] endif
));

% Three blocks constraint
constraint (forall(i,j,k in 1..n where i<j /\ j<k) (
	 if  x[i] == x[j] /\ widths[i] == widths[j] /\ y[i] == y[k] /\ heights[i] + heights[j] == heights[k]  then
	 				x[k] < x[i]
	 endif
));


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