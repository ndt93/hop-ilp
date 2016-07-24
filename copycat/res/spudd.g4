grammar spudd;

init
	: variablesBlock
	  initBlock?
	  actionBlock+
	  config+
	  ;

initBlock
	: 'init' '[*'
	      dtree+
	  ']'
	;

variablesBlock
	: '(variables' variable+ ')'
	;

variable : '(' ID node+ ')';

actionBlock
    : 'action' ID
          ttree+
          costBlock
      'endaction'
    ;

costBlock
	: 'cost' '[+'
	      dtree+
	   ']'
	;

config
	: rewardBlock
	| discount
	| horizon
	;

rewardBlock
	: 'reward' dtree ;

discount : 'discount' number ;

horizon : 'horizon' val=number ;

ttree : ID dtree ;

dtree
    : '(' node ')'
    | '(' node dtree ')'
    | '(' node dtree dtree ')'
    ;

node : ID | number | BOOL ;

number : INT | FLOAT ;

ID : [a-z][a-zA-Z0-9_']+ ;

BOOL : 'true' | 'false' ;

INT : [+-]? DIGIT+ ;

FLOAT : [+-]? DIGIT+ '.' DIGIT+ ;

fragment DIGIT : ('0'..'9') ;

WS : [ \t\r\n]+ -> skip ;