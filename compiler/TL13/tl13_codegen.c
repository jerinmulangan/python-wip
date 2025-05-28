// tl13_codegen.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "tl13_ast.h"
#include "tl13_symbol_table.h"

static const char* infer_type(ASTNode *node) {
    if (!node) return NULL;
    switch (node->kind) {
        case NODE_NUM:
        case NODE_READINT:
            return "int";
        case NODE_BOOL:
            return "bool";
        case NODE_IDENT: {
            SymbolEntry *e = find_symbol(node->value);
            if (!e) {
                fprintf(stderr, "warning: using undeclared variable %s; defaulting to int.\n", node->value);
                add_symbol(node->value, "int");
                e = find_symbol(node->value);
                printf("int %s = 0;\n", node->value);
            }
            if (!e->initialized) {
                fprintf(stderr, "warning: variable %s used before initialization.\n", node->value);
            }
            return e->type;
        }
        case NODE_BINARY_OP: {
            const char *lt = infer_type(node->left);
            const char *rt = infer_type(node->right);
            if (strcmp(node->value, "*")==0 || strcmp(node->value, "div")==0 || strcmp(node->value, "mod")==0 ||
                strcmp(node->value, "+")==0 || strcmp(node->value, "-")==0) {
                if (lt && rt && strcmp(lt, "int")==0 && strcmp(rt, "int")==0) return "int";
                fprintf(stderr, "type mismatch error: operator %s requires int operands.\n", node->value);
                exit(1);
            }
            if (strcmp(node->value, "=")==0 || strcmp(node->value, "!=")==0 ||
                strcmp(node->value, "<")==0 || strcmp(node->value, ">")==0 ||
                strcmp(node->value, "<=")==0 || strcmp(node->value, ">=")==0) {
                if (lt && rt && strcmp(lt, "int")==0 && strcmp(rt, "int")==0) return "bool";
                fprintf(stderr, "type mismatch error: comparison %s requires int operands.\n", node->value);
                exit(1);
            }
            fprintf(stderr, "type error: unknown operator %s.\n", node->value);
            exit(1);
        }
        default:
            return NULL;
    }
}

void generate_code(ASTNode *node) {
    if (!node) return;
    switch (node->kind) {
        case NODE_PROGRAM:
            printf("#include <stdio.h>\n#include <stdlib.h>\nint main() {\n");
            generate_code(node->left);
            generate_code(node->right);
            printf("return 0;\n}\n");
            break;

        case NODE_DECLARATION:
            if (!node->left || !node->left->value) break;
            printf("int %s = 0;\n", node->left->value);
            add_symbol(node->left->value, node->right ? node->right->value : "int");
            break;

        case NODE_ASSIGN: {
            const char *varName = node->value;
            if (!varName) {
                fprintf(stderr, "error: bad assignment.\n");
                return;
            }
            SymbolEntry *entry = find_symbol(varName);
            if (!entry) {
                fprintf(stderr, "warning: undeclared variable %s; defaulting to int.\n", varName);
                printf("int %s = 0;\n", varName);
                add_symbol(varName, "int");
                entry = find_symbol(varName);
            }
            ASTNode *rhs = node->right;
            const char *rt = infer_type(rhs);
            if (strcmp(entry->type, rt) != 0) {
                fprintf(stderr, "type mismatch: cannot assign %s to %s %s.\n", rt, entry->type, varName);
                exit(1);
            }
            set_initialized(varName);
            if (rhs->kind == NODE_READINT) {
                printf(
                    "if (scanf(\"%%d\", &%s) != 1) { fprintf(stderr, \"type mismatch error: non-integer input for %s.\\n\"); exit(1); }\n",
                    varName, varName
                );
            } else {
                printf("%s = ", varName);
                generate_code(rhs);
                printf(";\n");
            }
        } break;

        case NODE_WRITEINT: {
            const char *at = infer_type(node->left);
            if (strcmp(at, "int") != 0) {
                fprintf(stderr, "type Error: writeInt requires int, got %s.\n", at);
                exit(1);
            }
            printf("printf(\"%%d\\n\", "); generate_code(node->left); printf(");\n");
        } break;

        case NODE_BINARY_OP:
            generate_code(node->left); printf(" %s ", node->value); generate_code(node->right);
            break;

        case NODE_NUM:
        case NODE_BOOL:
        case NODE_IDENT:
            printf("%s", node->value);
            break;

        case NODE_IF: {
            const char *ct = infer_type(node->left);
            if (strcmp(ct, "bool") != 0) { fprintf(stderr, "type mismatch error: if requires bool, got %s.\n", ct); exit(1);}
            printf("if ("); generate_code(node->left); printf(") {\n");
            generate_code(node->right); printf("}\n");
        } break;

        case NODE_IF_ELSE: {
            const char *ct = infer_type(node->left);
            if (strcmp(ct, "bool") != 0) { fprintf(stderr, "type mismatch error: if requires bool, got %s.\n", ct); exit(1);}
            printf("if ("); generate_code(node->left); printf(") {\n");
            generate_code(node->right); printf("} else {\n");
            generate_code(node->extra); printf("}\n");
        } break;

        case NODE_WHILE: {
            const char *ct = infer_type(node->left);
            if (strcmp(ct, "bool") != 0) { fprintf(stderr, "type mismatch error: while requires bool, got %s.\n", ct); exit(1);}
            printf("while ("); generate_code(node->left); printf(") {\n");
            generate_code(node->right); printf("}\n");
        } break;

        case NODE_BLOCK:
            generate_code(node->left);
            break;

        default:
            break;
    }
    if (node->next) generate_code(node->next);
}
