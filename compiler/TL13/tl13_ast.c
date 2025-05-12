#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "tl13_ast.h"
ASTNode *root = NULL;

ASTNode *create_node(NodeKind kind, char *value, ASTNode *left, ASTNode *right, ASTNode *extra) {
    ASTNode *node = (ASTNode *)malloc(sizeof(ASTNode));
    node->kind = kind;
    node->value = value ? strdup(value) : NULL;
    node->left = left;
    node->right = right;
    node->extra = extra;
    node->next = NULL;
    return node;
}

const char *node_kind_to_string(NodeKind kind) {
    switch (kind) {
        case NODE_PROGRAM: return "Program";
        case NODE_DECLARATION: return "Declaration";
        case NODE_STATEMENT: return "Statement";
        case NODE_ASSIGN: return "Assignment";
        case NODE_EXPRESSION: return "Expression";
        case NODE_TYPE: return "Type";
        case NODE_BLOCK: return "Block";
        case NODE_IF: return "If";
        case NODE_IF_ELSE: return "IfElse";
        case NODE_WHILE: return "While";
        case NODE_WRITEINT: return "WriteInt";
        case NODE_READINT: return "ReadInt";
        case NODE_LITERAL: return "Literal";
        case NODE_VARIABLE: return "Variable";
        case NODE_BINARY_OP: return "BinaryOp";
        case NODE_BOOL: return "Boolean";
        case NODE_NUM: return "Number";
        case NODE_IDENT: return "Identifier";
        default: return "Unknown";
    }
}

void print_ast(ASTNode *node, int level) {
    if (!node) return;

    for (int i = 0; i < level; ++i) printf("  ");

    printf("Node kind: %s", node_kind_to_string(node->kind));
    if (node->value) {
        printf(" (value: %s)", node->value);
    }
    printf("\n");

    print_ast(node->left, level + 1);
    print_ast(node->right, level + 1);
    print_ast(node->extra, level + 1);
    print_ast(node->next, level);
}

/**
void print_ast(ASTNode *node, int level) {
    if (!node) return;
    for (int i = 0; i < level; ++i) printf("  ");
    printf("Node kind: %d", node->kind);
    if (node->value) printf(" (value: %s)", node->value);
    printf("\n");

    print_ast(node->left, level + 1);
    print_ast(node->right, level + 1);
    print_ast(node->extra, level + 1);
    print_ast(node->next, level);
}
*/
