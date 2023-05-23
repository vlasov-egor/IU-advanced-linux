#include <linux/init.h>
#include <linux/module.h>
#include <linux/device.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/vmalloc.h>
#include "device.h"

static int __init stack_dev_init(void)
{
    pr_info("Kernel module init\n");
    device_init();
    return 0;
}

static void __exit stack_dev_exit(void)
{
    pr_info("Kernel modulde exiting\n");
    device_uninit();
}

module_init(stack_dev_init);
module_exit(stack_dev_exit);
