#ifndef TL13_AST_H
#define TL13_AST_H

typedef enum {
    NODE_PROGRAM,
    NODE_DECLARATION,
    NODE_STATEMENT,
    NODE_ASSIGN,
    NODE_EXPRESSION,
    NODE_TYPE,
    NODE_BLOCK,
    NODE_IF,
    NODE_IF_ELSE,
    NODE_WHILE,
    NODE_WRITEINT,
    NODE_READINT,
    NODE_LITERAL,
    NODE_VARIABLE,
    NODE_BINARY_OP,
    NODE_BOOL,
    NODE_NUM,
    NODE_IDENT
} NodeKind;

typedef struct ASTNode {
    NodeKind kind;
    char *value;
    struct ASTNode* left;
    struct ASTNode* right;
    struct ASTNode* extra;
    struct ASTNode* next;
} ASTNode;

ASTNode* create_node(NodeKind kind, char *value, ASTNode* left, ASTNode* right, ASTNode* extra);

#endif
