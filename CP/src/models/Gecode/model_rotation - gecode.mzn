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
int: min_h = max (ceil(sum(areas)/ w), min(max(heights), max(widths)));


% Height we want to minimize
var min_h..max_h:  h;

% Coordinates of the bottom-left corner of each block
array[1..n] of var 0..w - min(widths ++ heights) : x;
array[1..n] of var 0..max_h - min(widths ++ heights): y;
array[1..n] of var 0..max(max_h,w) - min(widths ++ heights) : effective_width;
array[1..n] of var 0..max(max_h,w) - min(widths ++ heights) : effective_height;

% Placement constraints
constraint forall(i in 1..n) (x[i] + effective_width[i] <= w /\ y[i] + effective_height[i] <= h) ::bounds;

constraint forall (i in 1..n) ((effective_width[i] = widths[i] /\  effective_height[i] = heights[i]) \/ (effective_width[i] = heights[i] /\  effective_height[i] = widths[i]));

constraint forall (i in 1..n) (effective_width[i] <= w /\ effective_height[i] <= h);



%No overlapping global constraint
constraint diffn(x,y,effective_width,effective_height);

% Cumulative use of resources global constraint
constraint cumulative(x, effective_width, effective_height, h) ::domain;
constraint cumulative(y, effective_height, effective_width, w) ::domain;
% Symmetry breaking constraints

% If two blocks have the same dimensions, then the first one has to be closer to the origin ( coordinates (0,0) ).
constraint symmetry_breaking_constraint(forall(i,j in 1..n where i<j)(
		if effective_width[i] == effective_width[j] /\ effective_height[i] == effective_height[j] then
			(x[i] + y[i])  < (x[j] + y[j]) 
		endif
));


% I impose a given order for the first pair of elements.
constraint symmetry_breaking_constraint(x[1] + y[1] < x[2] + y[2]);

% Ordering for blocks with the same position on the y-axis and heieght
constraint symmetry_breaking_constraint(forall (i,j in 1..n where i<j) (
	( y[i] == y[j] /\ effective_height[i] == effective_height[j] ) -> x[i] < x[j]
));

% Three blocks constraint
constraint symmetry_breaking_constraint(forall(i,j,k in 1..n where i<j /\ j<k) (
	(x[i] == x[j] /\ effective_width[i] == effective_width[j] /\ y[i] == y[k] /\ effective_height[i] + effective_height[j] == effective_height[k] )-> x[k] < x[i])
);

ann: search_annotation = seq_search([
	int_search(y, smallest, indomain_min),
	int_search(x, first_fail, indomain_min), 
	int_search(effective_width, input_order, indomain_min),
	int_search(effective_height, input_order, indomain_min),
	int_search([h], input_order,indomain_min),     		
]) :: restart_luby(60) ::relax_and_reconstruct(y,50);


solve :: search_annotation minimize h;

output[show(w) ++
			" " ++
			show(h) ++
			"\n" ++
			show(n) ++
			"\n" ++
			show(effective_width) ++
			"\n" ++
			show(effective_height) ++
			"\n" ++
			show(x) ++ 
			"\n" ++
			show(y)
];