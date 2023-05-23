#include <linux/errno.h>
#include <linux/printk.h>
#include <linux/vmalloc.h>
#include <linux/module.h>
#include "stack.h"

int stack_init(struct Stack *stack)
{
    stack->capacity = STACK_SIZE;
    stack->head = 0;

    mutex_init(&stack->lock);
    stack->array = vmalloc(sizeof(int32_t) * STACK_SIZE);
    pr_info("STACK: Inited stack with capacity %ld", stack->capacity);
    return 0;
}

int stack_uninit(struct Stack *stack)
{
    vfree(stack->array);
    mutex_destroy(&stack->lock);
    pr_info("STACK: Uninitialized stack");
    return 0;
}

int stack_push(struct Stack *stack, int32_t value)
{
    pr_info("STACK: Pushing %d to stack", value);
    int ret = 0;
    mutex_lock(&stack->lock);
    do
    {
        if (stack->head == stack->capacity)
        {
            pr_info("STACK: Failed to push - stack is full");
            ret = -ENOBUFS;
            break;
        }
        stack->array[stack->head] = value;
        stack->head++;
    } while (0);

    mutex_unlock(&stack->lock);
    return ret;
}

static int stack_pop_impl(struct Stack *stack, int32_t *value)
{
    if (stack->head == 0)
    {
        pr_info("STACK: Failed to pop - stack is empty");
        return -ENOSPC;
    }

    stack->head--;
    *value = stack->array[stack->head];
    return 0;
}

int stack_pop(struct Stack *stack, int32_t *value)
{
    pr_info("Poping from stack");
    int ret = 0;
    mutex_lock(&stack->lock);
    do
    {
        ret = stack_pop_impl(stack, value);
    } while (0);

    mutex_unlock(&stack->lock);
    pr_info("Poped value %d", *value);
    return ret;
}

int stack_change_size(struct Stack *stack, size_t new_capacity)
{
    pr_info("STACK: Changing size from %lu to %lu", stack->capacity, new_capacity);
    int ret = 0;
    mutex_lock(&stack->lock);

    do
    {
        while (new_capacity < stack->head)
        {
            int32_t value;
            ret = stack_pop_impl(stack, &value);
            if (ret != 0)
                break;
        }

        int32_t *new_stack = (int32_t *)vmalloc(sizeof(new_stack[0]) * new_capacity);
        if (new_stack == NULL)
        {
            pr_err("STACK: Failed to allocate memory for changed stack");
            ret = -ENOMEM;
            break;
        }

        memcpy(new_stack, stack->array, stack->head * sizeof(stack->array[0]));
        vfree(stack->array);
        stack->array = new_stack;
        stack->capacity = new_capacity;
    } while (0);

    mutex_unlock(&stack->lock);
    return ret;
}