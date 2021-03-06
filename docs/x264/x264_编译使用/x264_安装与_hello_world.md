# x264 安装与 hello world

本过程参考了[此 csdn 文章](https://blog.csdn.net/martinkeith/article/details/105323052?utm_medium=distribute.pc_relevant.none-task-blog-title-3&spm=1001.2101.3001.4242)

## 1 x264 下载

从[官网](https://www.videolan.org/developers/x264.html)下载 x264 的源码

## 2 windows 安装过程

### 2.1 MSYS2 安装与启动

#### 2.1.1 说明

获得源码后，x264 的安装只需要如下两步（关于这两步的说明见[此网站](https://www.cnblogs.com/tinywan/p/7230039.html)，网站里面还有一步 `make install` 是将编译好的软件进行安装，但是 x264 没必要安装，所以不需要这步）

```bash
./configure --some-args
make
```

在 linux 中，以上两步可以直接执行，**在 windows 中则不行**，因此需要先安装 linux 终端环境的模拟软件 **MSYS2**

#### 2.1.2 安装步骤

1. 从 [MSYS2 官网](https://www.msys2.org/)或者[清华镜像站](https://mirrors.tuna.tsinghua.edu.cn/msys2/distrib/x86_64/)中下载 MSYS2 程序，需要记住安装路径

    安装完成之后会有三个 exe 和一个 cmd，如下图，三个 exe 的主要区别在于其打开时默认的环境配置不同，详见[此网站](https://hustlei.github.io/2018/11/msys2-for-win.html)，`msys2_shell.cmd` 可以自由选择打开哪个 exe，所以可以主要用这个 cmd 文件

    ![x264_安装与_hello_world_1372352512](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_1372352512.png)

2. 在安装完成之后，需要将安装目录加入系统环境变量，怎么加看[百度经验](https://jingyan.baidu.com/article/ca41422f17107a1eaf99ed64.html)
3. 在你需要打开 msys2 的目录的地址栏输入以下内容然后按回车，**前面 `D:\xxx` 需要更换为你自己的 msys2 的 cmd 文件位置**

    ```bash
    D:\msys64\msys2_shell.cmd -mingw64 -here
    ```

    如下图然后按回车

    ![x264_安装与_hello_world_6939828224](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_6939828224.png)

    如此可以打开指定的 msys2 的 exe 文件并自动将其工作目录设定为当前文件夹

    ![x264_安装与_hello_world_5513654272](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_5513654272.png)

4. （可跳过）如果你有自己的其它终端软件，不想使用 msys2 默认的 mintty，可以输入如下指令以直接在当前终端中打开 msys2

    ```bash
    D:\msys64\msys2_shell.cmd -defterm -no-start -mingw64 -here
    ```

    效果如下，直接在当前终端中打开

    ![x264_安装与_hello_world_4408830976](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_4408830976.png)

### 2.2 MinGW64 等环境安装

1. 将软件源更换为清华源

    按照[清华镜像站](https://mirrors.tuna.tsinghua.edu.cn/help/msys2/)的指示找到三个 mirrorlist 文件然后把清华源放到其它源前面，然后刷新即可

2. 通过以下指令在 MSYS2 中安装 MinGW64 以及其它必要环境（别复制 # 之后的内容）

    ```bash
    pacman -Syu # 同步软件库并更新系统到最新状态（升级核心包）
    pacman -Su # 升级其它包（非必须）
    pacman -S mingw-w64-x86_64-toolchain base-devel git nasm # 装环境
    ```

    大概一个多 G

### 2.3 build x264

1. 使用 msys2 进入 x264-master 文件夹，输入以下指令安装

    ```powershell
    mkdir build # 创建一个 build 文件夹
    cd build
    ../configure --host=x86_64-w64-mingw32 --enable-shared
    make
    ```

    关于 `configure` 选项的说明可以参考[此 csdn 博客](https://blog.csdn.net/CrystalShaw/article/details/92795584)

    如果出现以下错误

    ```bash
    ln: 无法创建符号链接 './Makefile': No such file or directory
    ```

    则将 x264-master 文件夹下的 configure 文件的第 1651 行的

    ```bash
    [ "$SRCPATH" != "." ] && ln -sf ${SRCPATH}/Makefile ./Makefile
    ```

    改为（或者你手动把 Makefile 文件复制过去也行）

    ```bash
    [ "$SRCPATH" != "." ] && cp -f ${SRCPATH}/Makefile ./Makefile
    ```

    之后删除 build 文件夹中的内容并重新编译

    编译成功之后可以在 build 文件夹下找到 x264 的 dll 文件（我这里文件名是 `libx264-161.dll`）和 exe 文件（文件名是 `x264.exe`），**两者均可以用来进行视频编码**，测试 exe 文件是否能够运行的方法比较简单，直接在终端里输入 `x264.exe` 调用即可，有输出报错“缺少输入文件”即是正常，测试 dll 文件的方法相对比较麻烦，下面有两种方法，一种是网上流传的把 dll 文件转成 lib 文件然后用 visual studio 调用，一种是直接调用 dll 文件测试，个人推荐后一种，因为相对而言比较方便

## 3 编译测试

### 3.1 Visual Studio 编译测试

1. 使用 pexports 将 dll 文件转为 lib 文件

    从[此链接](https://sourceforge.net/projects/mingw/files/MinGW/Extension/pexports/pexports-0.47/)下载 pexports，选 `pexports-0.47-mingw32-bin.tar.xz`，解压得到 exe，exe 放哪儿随意

    使用以下指令将 dll 文件转为 lib 文件，如果 pexports 存放的目录不在 `PATH` 里需要输入完整路径，第二条指令需要改成指向你自己安装的 Visual Studio 中的 `lib.exe`

    ```powershell
    pexports.exe libx264-161.dll > libx264-161.def
    "/c/Program Files (x86)/Microsoft Visual Studio/2019/Community/VC/Tools/MSVC/14.24.28314/bin/Hostx64/x64/lib.exe" /machine:x64 /def:libx264-161.def
    ```

    `libx264-161.def` 的完整内容如下

    ```
    LIBRARY libx264-161.dll
    EXPORTS
    x264_10_frame_pop
    x264_10_frame_push
    x264_10_frame_shift
    x264_10_frame_unshift
    x264_10_threadpool_delete
    x264_10_threadpool_init
    x264_10_threadpool_run
    x264_10_threadpool_wait
    x264_8_frame_pop
    x264_8_frame_push
    x264_8_frame_shift
    x264_8_frame_unshift
    x264_8_threadpool_delete
    x264_8_threadpool_init
    x264_8_threadpool_run
    x264_8_threadpool_wait
    x264_chroma_format DATA
    x264_cpu_detect
    x264_cpu_names DATA
    x264_cpu_num_processors
    x264_encoder_close
    x264_encoder_delayed_frames
    x264_encoder_encode
    x264_encoder_headers
    x264_encoder_intra_refresh
    x264_encoder_invalidate_reference
    x264_encoder_maximum_delayed_frames
    x264_encoder_open_161
    x264_encoder_parameters
    x264_encoder_reconfig
    x264_free
    x264_levels DATA
    x264_log_default
    x264_log_internal
    x264_malloc
    x264_mdate
    x264_nal_encode
    x264_param2string
    x264_param_apply_fastfirstpass
    x264_param_apply_profile
    x264_param_cleanup
    x264_param_default
    x264_param_default_preset
    x264_param_parse
    x264_picture_alloc
    x264_picture_clean
    x264_picture_init
    x264_reduce_fraction
    x264_reduce_fraction64
    x264_slurp_file
    x264_threading_init
    ```

2. 使用 Visual Studio 新建基于 c++ 的控制台程序

    ![x264_安装与_hello_world_148740096](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_148740096.png)

3. 把两个头文件 `x264.h` 和 `x264_config.h` 加入项目，把 cpp 文件的内容从 hello world 改成如下

    ```cpp
    #include <iostream>
    #include <string>
    #include "stdint.h"  
    #pragma comment(lib, "libx264-161.lib") // 注意这里 x264 的版本可能不一样，不是 161
    extern "C"
    {
    #include "x264.h"
    #include "x264_config.h"
    };
    using namespace std;
     
    int main(int argc, char **argv)
    {
    	x264_param_t param;
    	x264_param_default(&param);
    	cout << "hello,x264" << endl;
    	return 0;
    }
    ```

    项目结构大概如下

    ![x264_安装与_hello_world_9809903616](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_9809903616.png)

4. 右键生成项目

    ![x264_安装与_hello_world_5925983232](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_5925983232.png)

5. 在 VS 项目目录下的 debug 目录下找到生成的 exe 文件，**复制到与前面的 dll 文件和 lib 文件同一目录**

    ![x264_安装与_hello_world_4121250816](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_4121250816.png)

6. 打开 cmd 运行 exe 文件，得到输出

    ![x264_安装与_hello_world_1036368896](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_1036368896.png)

### 3.2 MSYS2 环境 GCC 编译测试

使用 Visual Studio 编译需要建立一个环境很麻烦，在 MSYS2 命令行下可以直接通过 Mingw64 中的 GCC 进行编译测试，仅需要 `.dll` 文件

首先进行编译

```bash
$ g++ libx264-161.dll test.cpp -o test.exe
```

然后执行

```bash
$ ./test.exe
hello,x264
```

需要注意此时需要在编译中引入 `.dll` 文件，这是由于 `test.c` 中的 `#param commit` 指令**不再适用**，这个指令的意义是让 **VS 的编译器**在连接时自动连接对应库，但是 **gcc  不支持在代码中添加自动连接指令**（见[此问题](https://stackoverflow.com/questions/3974070/linking-with-a-pragma-with-g)），必须在编译指令中手动指定连接对象

---

![x264_安装与_hello_world_8685399040](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_8685399040.png)