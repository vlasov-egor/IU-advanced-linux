#include <linux/stddef.h>
#include <linux/types.h>
#include <linux/mutex.h>

#ifndef STACK_SIZE
#define STACK_SIZE 10
#endif

struct Stack
{
    size_t capacity;
    int32_t *array;
    struct mutex lock;

    size_t head;
};

int stack_init(struct Stack *stack);
int stack_uninit(struct Stack *stack);

int stack_pop(struct Stack *stack, int32_t *value);
int stack_push(struct Stack *stack, int32_t value);
int stack_change_size(struct Stack *stack, size_t new_capacity);
