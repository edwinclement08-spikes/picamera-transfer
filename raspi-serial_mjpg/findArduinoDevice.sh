#!/bin/bash
ls /dev/tty* -1 | grep -v tty[0-9].* | grep -v tty$ | grep -v ttyAMA0 |grep -v printk
