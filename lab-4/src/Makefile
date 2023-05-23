ccflags-y := -std=gnu99 -Wno-declaration-after-statement

obj-m := stack_dev.o
stack_dev-y := ./src/stack_dev.o ./src/stack.o ./src/device.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules
clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
uninstall:
	rmmod stack_dev
install:
	insmod stack_dev.ko
test:
	pytest tests/test.py