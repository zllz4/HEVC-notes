# BUG：x264 加入新文件无法编译

## 1 概述

在 x264 中添加新函数有两种方式，一种是在原代码 `.c` 文件（如 `encoder.c`）中直接加入，在对应的 `.h` 文件中申明，另一种是新建一个 `.c` 文件存放你的新函数，然后新建一个 `.h` 文件进行申明，然后在需要用到这个函数的时候 include 你新建的 `.h` 文件，后者有一个坑，就是需要修改 x264 的 `Makefile`，否则无法通过编译，以下介绍修改步骤

## 2 Bug 复现步骤

首先新建 `my_func` 文件夹，在此文件夹下新增 `my_func.c` 和 `my_func.h` 文件，这两个文件定义了一个 `x264_hello` 函数，可以输出 hello world，如下

```c
void x264_hello(x264_t* h)
{
    x264_log(h, X264_LOG_INFO, "Hello World!\n");
}
```

之后在 `encoder.c` 中的 `x264_encoder_encode` 函数中引用这个函数

```c
x264_hello(h);
```

同时引入头文件

```c
#include "my_func/my_func.h"
```

在 `build` 文件夹下通过 `make` 尝试编译（编译方法见 [x264 安装与 hello world]）会报如下错误

```c
D:/msys64/mingw64/bin/../lib/gcc/x86_64-w64-mingw32/10.2.0/../../../../x86_64-w64-mingw32/bin/ld.exe: libx264.a(encoder-8.o): in function `x264_8_encoder_encode':
C:\Users\admin\Desktop\x264\x264-work\build/../encoder/encoder.c:3505: undefined reference to `x264_hello'
D:/msys64/mingw64/bin/../lib/gcc/x86_64-w64-mingw32/10.2.0/../../../../x86_64-w64-mingw32/bin/ld.exe: libx264.a(encoder-10.o): in function `x264_10_encoder_encode':
C:\Users\admin\Desktop\x264\x264-work\build/../encoder/encoder.c:3505: undefined reference to `x264_hello'
collect2.exe: error: ld returned 1 exit status
make: *** [Makefile:267：x264.exe] 错误 1
```

## 3 解决方案

这个错误主要是由于 **`my_func.c` 没有自动被编译成** **`my_func.o` 文件**，因为这个 `.c` 文件是你新加的，`Makefile` 并不认识这个新文件，所以不会帮你编译

解决方法是在 `Makefile` 的如下字段前加上一句

```makefile
# 加上下面两句之一
OBJS += my_func/my_func-8.o
# OBJS += my_func/my_func-10.o # 当输入视频比特深度为 10 时加这个 

# 生成 libx264.a 的主要代码段
$(LIBX264): $(GENERATED) .depend $(OBJS) $(OBJASM)
	rm -f $(LIBX264)
	$(AR)$@ $(OBJS) $(OBJASM)
	$(if $(RANLIB), $(RANLIB) $@)
```

`OBJS` 里面是编码生成 `libx264.a` 所依赖的 `.o` 文件，根据 `Makefile` 的设置，后缀为 `-8.o` 的文件会自动被 `Makefile` 从同名的 `.c` 文件编译并设置宏 `BIT_DEPTH` 为 `8`，后缀为 `-10.o` 的文件会自动被 `Makefile` 从同名 `.c` 文件编译并设置宏 `BIT_DEPTH` 为 `10`，也就是 `my_func/my_func.c` 将被编译为 `my_func-8.o` 或者 `my_func-10.o`，之后编译成的 `.o` 文件将被用来生成 `libx264.a`

进行以上修改后编译可以正常进行，编译好的程序在编码时可以输出 hello world

```makefile
x264 [info]: Hello World!
x264 [info]: Hello World!
x264 [info]: Hello World!
x264 [info]: Hello World!
x264 [info]: Hello World!
```