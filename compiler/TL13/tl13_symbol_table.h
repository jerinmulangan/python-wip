// tl13_symbol_table.h
#ifndef TL13_SYMBOL_TABLE_H
#define TL13_SYMBOL_TABLE_H

typedef struct SymbolEntry {
    char *name;
    char *type;
    int initialized;
    struct SymbolEntry *next;
} SymbolEntry;

void add_symbol(const char *name, const char *type);
SymbolEntry *find_symbol(const char *name);
void set_initialized(const char *name);
void print_symbol_table();

#endif
