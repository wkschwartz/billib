#ifndef llrbt_h_INCLUDED
#define llrbt_h_INCLUDED

#define KEY void *
#define VALUE void *
#define LLRBT_ITER_ERROR -2

enum node_color { BLACK, RED };

/* key comparison functions. -1 means a < b; 0 means a == b; 1 means a > b */
typedef int (*keycmp)(KEY, KEY);
/* Functions to free key & value objects; they must not crash on NULL input */
typedef void (*keyfree)(KEY) keyfree;
typedef void (*valuefree)(VALUE);
/* Memory allocator (malloc) and deallocator (free) types */
typedef (void *) (*mem_alloc)(size_t);
typedef void (*mem_free)(void *);

typedef struct llrbt BinaryTree;
typedef struct llrbt_iter BinaryTreeIterator;

BinaryTree * llrbt_new(keycmp cmp, mem_alloc mem_alloc, mem_free mem_free, keyfree keyfree, valuefree valuefree);
void   llrbt_free(BinaryTree *t);
VALUE  llrbt_get(BinaryTree *t, KEY key);
void   llrbt_insert(BinaryTree *t, KEY key, VALUE value);
size_t llrbt_len(BinaryTree *t);
void   llrbt_clear(BinaryTree *t);
void   llrbt_deletemin(BinaryTree *t);
struct node * llrbt_delete(BinaryTree *t, KEY key);
BinaryTreeIterator * llrbt_iter(BinaryTree *t, int reversed);
void llrbt_iter_free(BinaryTreeIterator *iter);
struct node * llrbt_iter_next(BinaryTreeIterator *iter);
int llrbt_iter_hasnext(BinaryTreeIterator *iter);

#endif
