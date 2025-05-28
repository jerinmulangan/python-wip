%{
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "tl13_ast.h"
#include "tl13.tab.h"

extern int yylineno;

%}

%option noyywrap nounput noinput yylineno

blanks            [ \r\t\n]+
comments          [#][^\n\r]*
num               [1-9][0-9]*|0
boollit           true|false
ident             [A-Za-z][A-Za-z0-9]*

%%

{blanks}          { /* ignore */ }
{comments}        { /* ignore */ }

"if"              { return IF; }
"then"            { return THEN; }
"else"            { return ELSE; }
"begin"           { return BEGIN_BLOCK; }
"end"             { return END_BLOCK; }
"while"           { return WHILE; }
"do"              { return DO; }
"program"         { return PROGRAM; }
"var"             { return VAR; }
"as"              { return AS; }
"int"             { return INT; }
"bool"            { return BOOL; }
"writeInt"        { return WRITEINT; }
"readInt"         { return READINT; }

"("               { return LP; }
")"               { return RP; }
":="              { return ASGN; }
";"               { return SC; }

"*"               { yylval.sval = strdup(yytext); return OP2; }
"div"             { yylval.sval = strdup(yytext); return OP2; }
"mod"             { yylval.sval = strdup(yytext); return OP2; }

[\+\-]            { yylval.sval = strdup(yytext); return OP3; }

"="               { yylval.sval = strdup(yytext); return OP4; }
"!="              { yylval.sval = strdup(yytext); return OP4; }
"<"               { yylval.sval = strdup(yytext); return OP4; }
">"               { yylval.sval = strdup(yytext); return OP4; }
"<="              { yylval.sval = strdup(yytext); return OP4; }
">="              { yylval.sval = strdup(yytext); return OP4; }

{num}             {
                    yylval.sval = strdup(yytext);
                    return NUM;
                  }
{boollit}         {
                    yylval.sval = strdup(yytext);
                    return BOOLLIT;
                  }
{ident}           {
                    yylval.sval = strdup(yytext);
                    return IDENT;
                  }

.                 {
                    fprintf(stderr, "lexer got an error: unexpected character '%s' on line %d\n", yytext, yylineno);
                    return -1; 
                  }

%%
