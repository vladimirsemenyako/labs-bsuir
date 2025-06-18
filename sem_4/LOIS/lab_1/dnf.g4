grammar dnf;

dnf: OPB disjunction CLB EOF
   | disjunction EOF
   ;

disjunction
    : conjunction (OR conjunction)*
    | OPB disjunction CLB
    ;

conjunction
    : literal (AND literal)*
    | OPB conjunction CLB
    ;

literal
    : VAR
    | OPB NOT VAR CLB
    ;

VAR: [A-Z];
OR: '\\/';
AND: '/\\';
NOT: '!';
OPB: '(';
CLB: ')';

WS: [ \t\r\n]+ -> skip;