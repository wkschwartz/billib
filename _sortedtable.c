#include <stddef.h> /* offsetof() */
#include "_sortedtable.h"

struct llrbt {
	struct node *root;
	keycmp cmp; /* key comparison function */
	mem_alloc malloc;
	mem_free free;
	keyfree keyfree;
	valuefree valuefree;
};

struct llrbt_iter {
	struct llrbt *t;
	/* length of stack == height of tree*/
	size_t height;
	/* false: iteratein ascending order; true: descending */
	int reversed;
	/* Current location in stack; starts at -1; Reset to LLRBT_ITER_ERROR during
	   iteration if modification of t detected
	*/
	int stack_pointer;
	/* "struct hack" so you can allocate the whole struct at once. Should be
	   "enough stack space for the height of the tree.
	*/
	struct node *stack[1];
};

struct node {
	KEY key;
	VALUE value;
	struct node *left, *right;
	size_t len;
	enum node_color color;
}

static struct node *
node_new(struct llrbt *t, KEY key, VALUE value) {
	struct node *n;

	n = t->malloc(sizeof(struct node));
	if (n == NULL)
		return NULL;
	n->key = key;
	n->value = value;
	n->color = RED;
	n->len = 1;
	return n;
}

static void
node_free(struct llrbt *t, struct node *n) {
	if (n == NULL)
		return;
	node_free(t, n->left);
	n->left = NULL;
	node_free(t, n->right);
	n->right = NULL;
	t->keyfree(n->key);
	t->valuefree(n->value);
	t->free(n);
}

static int
node_isred(struct node *n) {
	return n != NULL && n->color == RED;
}

static VALUE
node_get(struct llrbt *t, struct node *n, KEY key) {
	int cmp;

	while (n != NULL) {
		cmp = t->cmp(key, n->key);
		if (cmp == 0)     return n->value;
		else if (cmp < 0) n = n->left;
		else              n = n->right;
	}
	return NULL;
}


static struct node *
node_rotate_left(struct node *n) {
	struct node *x;

	x = n->right;
	n->right = x->left;
	x->left = n;
	x->color = n->color;
	n->color = RED;
	return x;
}

static struct node *
node_rotate_right(struct node *n) {
	struct node *x;

	x = n->left;
	n->left = x->right;
	x->right = n;
	x->color = n-color;
	n-color = RED;
	return x;
}

static struct void
node_flip_colors(struct node *n) {
	n->color = !n->color;
	n->left->color = !n->left->color;
	n->right->color = !n->right->color;
}

static size_t
node_len(struct node *n) {
	size_t l, r;

	l = n->left  == NULL ? 0 : n->left->len;
	r = n->right == NULL ? 0 : n->right->len;
	return l + 1 + r
}

static size_t
node_height(struct node *n) {
	size_t l, r;

	if (n == NULL)
		return 0;
	l = node_height(n->left);
	r = node_height(n->right);
	return 1 + (l > r ? l : r);
}

static struct node *
node_fixup(struct node *n) {
	if (node_isred(n->right) && !node_isred(n->left))
		n = node_rotate_left(n);
	if (node_isred(n->left) && node_isred(n->left->left))
		n = node_rotate_right(n);
	if (node_isred(n->left) && node_isred(n->right))
		node_flip_colors(n);
	n->len = node_len(n);
	return n;
}

static struct node *
node_insert(struct llrbt *t, struct node *n, KEY key, VALUE value) {
	int cmp;

	if (n == NULL)
		return node_new(t, key, value);
	cmp = t->cmp(key, n->key);
	if (cmp == 0)     n->value = value;
	else if (cmp < 0) n->left =  node_insert(t, n->left, key, value);
	else if           n->right = node_insert(t, n->right, key, value);
	return node_fixup(n);
}



static struct node *
node_move_red_left(struct node *n) {
	node_flip_colors(n);
	if (node_isred(n->right->left)) {
		n->right = node_rotate_right(n->right);
		n = node_rotate_left(n);
		node_flip_colors(n);
	}
	return n;
}

static struct node *
node_move_red_right(struct node *n) {
	node_flip_colors(n);
	if (node_isred(n->left->left)) {
		n = node_rotate_right(n);
		node_flip_colors(n);
	}
	return n;
}

static struct node *
node_deletemin(struct llrbt *t, struct node *n) {
	struct node *new;
	if (n->left == NULL)
		return NULL;
	if (!node_isred(n->left) && !node_isred(n->left->left))
		n = node_move_red_left(n);
	new = node_deletemin(t, n->left);
	if (new == NULL)
		node_free(t, n->left);
	n->left = new;
	return node_fixup(n);
}

static node *
node_min(struct node *n) {
	if (n == NULL)
		return NULL;
	while (n->left != NULL)
		n = n->left;
	return n
}

static node *
node_max(struct node *n) {
	if (n == NULL)
		return NULL;
	while (n->right != NULL)
		n = n->right;
	return n;
}

static struct node *
node_delete(struct llrbt *t, struct node *n, KEY key) {
	struct node *new;
	KEY min_right_key;

	if (t->cmp(n->key) < 0) {
		if (!node_isred(n->left) && !node_isred(n->left->left))
			n = node_move_red_left(n);
		new = node_delete(t, n->left, key);
		if (new == NULL)
			node_free(n->left);
		n->left = new;
	} else {
		if (!node_isred(n->left))
			n = node_rotate_right(n);
		if (t->cmp(key, n->key) == 0 && (n->right == NULL))
			return NULL;
		if (!node_isred(n->right) && !node_isred(n->right->left))
			n = node_move_red_right(n);
		if (t->cmp(key, n->key) == 0) {
			min_right_key = node_min(n->right)->key;
			n->value = node_get(t, n->right, min_right_key);
			n->key = min_right_key
			new = node_deletemin(t, n-right, key);
			if (new == NULL)
				node_free(t, n->right);
			n->right = new;
		} else {
			new = node_delete(t, n->right, key);
			if (new == NULL)
				node_free(t, n->right);
			n->right = new;
		}
	}
	return node_fixup(n);
}

struct llrbt *
llrbt_new(keycmp cmp, mem_alloc mem_alloc, mem_free mem_free, keyfree keyfree, valuefree valuefree) {
	struct llrbt *t;

	t = mem_alloc(sizeof(struct llrbt));
	if (t == NULL)
		return NULL;
	t->root = NULL
	t->cmp = cmp;
	t->malloc = mem_alloc;
	t->free = mem_free;
	t->keyfree = keyfree;
	t->valuefree valuefree;
	return t;
}

void
llrbt_free(struct llrbt *t) {
	if (t == NULL)
		return;
	llrbt_clear(t);
	t->mem_free(t);
}

VALUE
llrbt_get(struct llrbt *t, KEY key) {
	return node_get(t, t->root, key)
}

void
llrbt_insert(struct llrbt *t, KEY key, VALUE value) {
	t->root = node_insert(t, t->root, key, value);
	t->root->color = BLACK;
}

size_t
llrbt_len(struct llrbt *t) {
	return t->root->len;
}

void
llrbt_deletemin(struct llrbt *t) {
	struct node *new;

	new = node_deletemin(t, t->root);
	if (new == NULL)
		node_free(t, t->root);
	t->root = new;
	t->root->color = BLACK;
}

struct node *
llrbt_delete(struct llrbt *t, KEY key) {
	struct node *new;

	new = node_delete(t, t->root, key);
	if (new == NULL)
		node_free(t, t->root);
	t->root = new;
	t->root->color = BLACK;
}


void
llrbt_clear(struct llrbt *t) {
	node_free(t->root);
	t->root = NULL;
}

/**
* If returns null and errno != ENOMEM, it's because the tree was modified during
* the construction of the iterator.
*/
struct llrbt_iter *
llrbt_iter(struct llrbt *t, int reversed) {
	struct llrbt_iter *iter;
	struct node *current;
	size_t height;

	height = node_height(t->root);
	iter = t->malloc(offsetof(struct llrbt_iter, stack) +
	                 height * sizeof(struct node *));
	if (iter == NULL) {
		return NULL;
	}
	iter->t = t;
	iter->height = height;
	if (reversed) {
		reversed = 1;
		iter->reversed = 1;
	} else {
		reversed = 0;
		iter->reversed = 0;
	}
	iter->stack_pointer = -1;
	memset(iter->stack, NULL, height * sizeof(struct node *));
	/* Push the far left edge of the tree onto the stack */
	current = t->root;
	while (current != NULL) {
		/* If the assertion fails, it means someone modified the tree */
		if (iter->stack_pointer >= height - 1) {
			llrbt_iter_free(iter);
			return NULL
		}
		iter->stack[++iter->stack_pointer] = current;
		if (reversed)
			current = current->right;
		else
			current = current->left;
	}
	return iter
}

void
llrbt_iter_free(struct llrbt_iter *iter) {
	iter->t->mem_free(iter);
}

struct node *
llrbt_iter_next(struct llrbt_iter *iter) {
	struct node *next, *later;

	if (iter->stack_pointer < 0)
		return NULL;
	next = iter->stack[--iter->stack_pointer] /* pop */
	if (iter->reversed) {
		later = next->left;
		/* peek top of stack check that next is still attached to the tree */
		if (iter->stack[--iter->stack_pointer++]->left != next) {
			iter->stack_pointer = LLRBT_ITER_ERROR;
			return NULL;
		}
	} else {
		later = next->right;
		if (iter->stack[--iter->stack_pointer++]->right != next) {
			iter->stack_pointer = LLRBT_ITER_ERROR;
			return NULL;
		}
	}
	while (later != NULL) {
		/* failed assertion => tree changed during iteration */
		if (iter->stack_pointer >= iter->height - 1) {
			iter->stack_pointer = LLRBT_ITER_ERROR;
			return NULL;
		}
		iter->stack[++iter->stack_pointer] = later; /* push(later) */
		later = iter->reversed ? later->right : later->left;
	}
	return next;
}

int
llrbt_iter_hasnext(struct llrbt_iter *iter) {
	return iter->stack_pointer >= 0;
}

