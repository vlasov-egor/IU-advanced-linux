#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/module.h>
#include <linux/ioctl.h>
#include "device.h"
#include "stack.h"

static struct Stack stack;

static int majorNumber;
static struct class *ebbcharClass = NULL;
static struct device *ebbcharDevice = NULL;

static int dev_open(struct inode *, struct file *);
static int dev_release(struct inode *, struct file *);
static ssize_t dev_read(struct file *, char *, size_t, loff_t *);
static ssize_t dev_write(struct file *, const char *, size_t, loff_t *);
static long dev_ioctl(struct file *file, unsigned int cmd, unsigned long arg);

static struct file_operations fops = {
    .open = dev_open,
    .read = dev_read,
    .write = dev_write,
    .release = dev_release,
    .unlocked_ioctl = dev_ioctl};

int device_init()
{
    stack_init(&stack);

    majorNumber = register_chrdev(0, DEVICE_NAME, &fops);
    if (majorNumber < 0)
    {
        pr_alert("Failed to register a major number\n");
        return majorNumber;
    }
    pr_info("Registered correctly with major number %d\n", majorNumber);

    // Register the device class
    ebbcharClass = class_create(THIS_MODULE, CLASS_NAME);
    if (IS_ERR(ebbcharClass))
    {
        unregister_chrdev(majorNumber, DEVICE_NAME);
        pr_alert("Failed to register device class");
        return PTR_ERR(ebbcharClass);
    }
    pr_info("Device class registered correctly");

    // Register the device driver
    ebbcharDevice = device_create(ebbcharClass, NULL, MKDEV(majorNumber, 0), NULL, DEVICE_NAME);
    if (IS_ERR(ebbcharDevice))
    {
        class_destroy(ebbcharClass);
        unregister_chrdev(majorNumber, DEVICE_NAME);
        pr_alert("Failed to create the device");
        return PTR_ERR(ebbcharDevice);
    }
    pr_info("Device class created correctly");
    return 0;
}

void device_uninit()
{
    device_destroy(ebbcharClass, MKDEV(majorNumber, 0));
    class_unregister(ebbcharClass);
    class_destroy(ebbcharClass);
    unregister_chrdev(majorNumber, DEVICE_NAME);

    stack_uninit(&stack);
    pr_info("Device uninitialized\n");
}

static int dev_open(struct inode *inodep, struct file *filep)
{
    pr_info("Device has been opened");
    return 0;
}

static ssize_t dev_read(struct file *filep, char *buf, size_t count, loff_t *offset)
{
    int actually_written = 0;
    int ret = 0;

    char *cur_buf = buf;
    size_t i = 0;
    for (i = 0; i < count / sizeof(int32_t); i++)
    {
        int32_t value = 0;
        ret = stack_pop(&stack, &value);

        if (ret != 0)
        {
            pr_info("STACK: Failed to pop %d", ret);
            break;
        }
        pr_info("Read value %d from stack", value);
        actually_written++;
        long retl = copy_to_user(cur_buf, &value, sizeof(int32_t));
        if (retl != 0)
        {
            return -EFAULT;
        }
        cur_buf += sizeof(int32_t);
    }

    return actually_written != 0 ? actually_written * sizeof(int32_t) : ret;
}

static ssize_t dev_write(struct file *filep, const char *buf, size_t len, loff_t *offset)
{
    pr_info("Wrtie op of len %lu", len);
    char *buffer = vmalloc(len);
    if (buffer == NULL)
    {
        pr_err("Buffer is null");
        return -EFAULT;
    }

    long retl = copy_from_user(buffer, buf, len);
    if (retl != 0)
    {
        pr_err("Failed to copy from user, %lu", retl);
        vfree(buffer);
        return -EFAULT;
    }

    size_t written = 0;
    bool failed = false;

    size_t i;
    char *cur_buf = buffer;
    int ret = 0;
    for (i = 0; i < len / sizeof(int32_t); i++)
    {
        ret = stack_push(&stack, *((int32_t *)cur_buf));
        if (ret != 0)
        {
            failed = true;
            break;
        }
        cur_buf += sizeof(int32_t);
        written += sizeof(int32_t);
    }

    // If not aligned byte remaining - augment it with zeros at the end.
    // In fact there will be no difference since I have little endian on my machine
    if (len % sizeof(int32_t) != 0)
    {
        int32_t number = 0;
        memcpy(&number, cur_buf, len % sizeof(int32_t));
        ret = stack_push(&stack, number);
        if (ret != 0)
        {
            failed = true;
        }
        else
        {
            written += len % sizeof(int32_t);
        }
    }

    vfree(buffer);
    return written == 0 && failed ? ret : written;
}

static int dev_release(struct inode *inodep, struct file *filep)
{
    pr_info("Device successfully closed\n");
    return 0;
}

#define CHANGE_STACK_IOCTL _IOW('a', 1, int32_t *)

static long dev_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
    pr_info("IOCTL with cmd=%x", cmd);
    if (cmd == CHANGE_STACK_IOCTL)
    {
        pr_info("IOCTL command for change stack size, arg=%lu", arg);
        int ret = stack_change_size(&stack, arg);
        return ret;
    }
    else
    {
        pr_err("Unknown IOCTL command: %u", cmd);
        return -EINVAL;
    }
    return 0;
}