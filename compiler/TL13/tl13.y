// tl13.y
%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "tl13_ast.h"
#include "tl13_codegen.h"

extern ASTNode* root;
extern int yylineno;
extern int yylex(void);
extern char *yytext;
int yyerror(char *s);
%}

%union {
    int ival;
    char* sval;
    ASTNode* node;
}

%token PROGRAM VAR AS INT BOOL
%token WRITEINT READINT
%token IF THEN ELSE BEGIN_BLOCK END_BLOCK WHILE DO
%token LP RP ASGN SC
%token <sval> NUM BOOLLIT IDENT OP2 OP3 OP4

%left OP4
%left OP3
%left OP2
%nonassoc IFX ELSE

%type <node> program declarations declaration statements statement
%type <node> if_statement ifelse_statement while_statement block
%type <node> expression
%type <sval> type

%start program

%%

program:
    PROGRAM declarations BEGIN_BLOCK statements END_BLOCK {
        root = create_node(NODE_PROGRAM, NULL, $2, $4, NULL);
    }
;

declarations:
    /* empty */ { $$ = NULL; }
  | declarations declaration {
        ASTNode *curr = $1;
        while (curr && curr->next) curr = curr->next;
        if (curr) curr->next = $2;
        else $$ = $2;
        $$ = $1 ? $1 : $2;
    }
;

declaration:
    VAR IDENT AS type SC {
        ASTNode *varNode  = create_node(NODE_IDENT,  $2, NULL, NULL, NULL);
        ASTNode *typeNode = create_node(NODE_TYPE,   $4, NULL, NULL, NULL);
        $$ = create_node(NODE_DECLARATION, NULL, varNode, typeNode, NULL);
        free($2);
    }
;

type:
    INT  { $$ = "int"; }
  | BOOL { $$ = "bool"; }
;

statements:
    /* empty */ { $$ = NULL; }
  | statements statement {
        ASTNode *curr = $1;
        while (curr && curr->next) curr = curr->next;
        if (curr) curr->next = $2;
        else $$ = $2;
        $$ = $1 ? $1 : $2;
    }
;

statement:
    IDENT ASGN READINT SC {
        ASTNode *idNode  = create_node(NODE_IDENT, $1, NULL, NULL, NULL);
        $$ = create_node(NODE_ASSIGN, $1, idNode,
                         create_node(NODE_READINT, NULL, NULL, NULL, NULL), NULL);
        free($1);
    }
  | IDENT ASGN expression SC {
        ASTNode *idNode  = create_node(NODE_IDENT, $1, NULL, NULL, NULL);
        $$ = create_node(NODE_ASSIGN, $1, idNode, $3, NULL);
        free($1);
    }
  | if_statement      { $$ = $1; }
  | ifelse_statement  { $$ = $1; }
  | while_statement   { $$ = $1; }
  | WRITEINT expression SC {
        $$ = create_node(NODE_WRITEINT, NULL, $2, NULL, NULL);
    }
  | block SC          { $$ = $1; }
;

if_statement:
    IF expression THEN statements END_BLOCK SC %prec IFX {
        $$ = create_node(NODE_IF, NULL, $2, $4, NULL);
    }
;

ifelse_statement:
    IF expression THEN statements ELSE statements END_BLOCK SC {
        $$ = create_node(NODE_IF_ELSE, NULL, $2, $4, $6);
    }
;

while_statement:
    WHILE expression DO statements END_BLOCK SC {
        $$ = create_node(NODE_WHILE, NULL, $2, $4, NULL);
    }
;

block:
    BEGIN_BLOCK statements END_BLOCK {
        $$ = create_node(NODE_BLOCK, NULL, $2, NULL, NULL);
    }
;

expression:
    expression OP4 expression { $$ = create_node(NODE_BINARY_OP, $2, $1, $3, NULL); free($2); }
  | expression OP3 expression { $$ = create_node(NODE_BINARY_OP, $2, $1, $3, NULL); free($2); }
  | expression OP2 expression { $$ = create_node(NODE_BINARY_OP, $2, $1, $3, NULL); free($2); }
  | NUM      { $$ = create_node(NODE_NUM,   $1, NULL, NULL, NULL); }
  | BOOLLIT  { $$ = create_node(NODE_BOOL,  $1, NULL, NULL, NULL); }
  | IDENT    { $$ = create_node(NODE_IDENT, $1, NULL, NULL, NULL); free($1); }
  | LP expression RP { $$ = $2; }
;

%%

int yyerror(char *s) {
    fprintf(stderr, "syntax Error: %s near '%s' on line %d\n", s, yytext, yylineno);
    return 1;
}

int main() {
    if (yyparse() == 0 && root) {
        generate_code(root);
    }
    return 0;
}
