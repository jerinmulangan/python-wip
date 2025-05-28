// tl13_symbol_table.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "tl13_symbol_table.h"

static SymbolEntry *symbol_table = NULL;

void add_symbol(const char *name, const char *type) {
    if (find_symbol(name)) return;
    SymbolEntry *entry = (SymbolEntry *)malloc(sizeof(SymbolEntry));
    entry->name = strdup(name);
    entry->type = strdup(type);
    entry->initialized = 0;
    entry->next = symbol_table;
    symbol_table = entry;
}

SymbolEntry *find_symbol(const char *name) {
    SymbolEntry *current = symbol_table;
    while (current) {
        if (strcmp(current->name, name) == 0) return current;
        current = current->next;
    }
    return NULL;
}

void set_initialized(const char *name) {
    SymbolEntry *entry = find_symbol(name);
    if (entry) entry->initialized = 1;
}

void print_symbol_table() {
    SymbolEntry *current = symbol_table;
    printf("\nsymbol Table:\n");
    while (current) {
        printf("%s: type=%s, initialized=%d\n", current->name, current->type, current->initialized);
        current = current->next;
    }
}
