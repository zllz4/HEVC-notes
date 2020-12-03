# x264 安装与 hello world

本过程参考了[此 csdn 文章](https://blog.csdn.net/martinkeith/article/details/105323052?utm_medium=distribute.pc_relevant.none-task-blog-title-3&spm=1001.2101.3001.4242)

## 1 x264 下载

从[官网](https://www.videolan.org/developers/x264.html)下载 x264 的源码

## 2 windows 安装过程

### 2.1 MSYS2 安装与启动

#### 2.1.1 说明

获得源码后，x264 的安装只需要如下三步（关于这三步的说明见[此网站](https://www.cnblogs.com/tinywan/p/7230039.html)）

```bash
./configure
make
make install
```

在 linux 中，以上三步可以直接执行，**在 windows 中则不行**，因此需要先安装 linux 终端环境的模拟软件 **MSYS2**

#### 2.1.2 安装步骤

1. 从 [MSYS2 官网](https://www.msys2.org/)或者[清华镜像站](https://mirrors.tuna.tsinghua.edu.cn/msys2/distrib/x86_64/)中下载 MSYS2 程序，需要记住安装路径

    安装完成之后会有三个 exe 和一个 cmd，如下图，三个 exe 的主要区别在于其打开时默认的环境配置不同，详见[此网站](https://hustlei.github.io/2018/11/msys2-for-win.html)，`msys2_shell.cmd` 可以自由选择打开哪个 exe，所以可以主要用这个 cmd 文件

    ![x264_安装与_hello_world_719](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_719.png)

2. 在安装完成之后，需要将安装目录加入系统环境变量，怎么加看[百度经验](https://jingyan.baidu.com/article/ca41422f17107a1eaf99ed64.html)
3. 在你需要打开 msys2 的目录的地址栏输入以下内容然后按回车，**前面 `D:\xxx` 需要更换为你自己的 msys2 的 cmd 文件位置**

    ```bash
    D:\msys64\msys2_shell.cmd -mingw64 -here
    ```

    如下图然后按回车

    ![x264_安装与_hello_world_4767](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_4767.png)

    如此可以打开指定的 msys2 的 exe 文件并自动将其工作目录设定为当前文件夹

    ![x264_安装与_hello_world_559](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_559.png)

4. （可跳过）如果你有自己的其它终端软件，不想使用 msys2 默认的 mintty，可以输入如下指令以直接在当前终端中打开 msys2

    ```bash
    D:\msys64\msys2_shell.cmd -defterm -no-start -mingw64 -here
    ```

    效果如下，直接在当前终端中打开

    ![x264_安装与_hello_world_4924](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_4924.png)

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

    如果它报一个 ln 什么什么 ./Makefile 的错你就手动把 Makefile 复制到 build 文件夹然后再 `make`

    成功之后可以在 build 文件夹下找到 x264 的 dll 文件

    ![x264_安装与_hello_world_5881](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_5881.png)

2. 使用 pexports 将 dll 文件转为 lib 文件

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

## 3 Visual Studio 编译测试

1. 使用 Visual Studio 新建基于 c++ 的控制台程序

    ![x264_安装与_hello_world_6759](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_6759.png)

2. 把两个头文件 `x264.h` 和 `x264_config.h` 加入项目，把 cpp 文件的内容从 hello world 改成如下

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

    ![x264_安装与_hello_world_4053](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_4053.png)

3. 右键生成项目

    ![x264_安装与_hello_world_6755](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_6755.png)

4. 在 VS 项目目录下的 debug 目录下找到生成的 exe 文件，**复制到与前面的 dll 文件和 lib 文件同一目录**

    ![x264_安装与_hello_world_1201](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_1201.png)

5. 打开 cmd 运行 exe 文件，得到输出

    ![x264_安装与_hello_world_945](markdown_images/x264_%E5%AE%89%E8%A3%85%E4%B8%8E_hello_world_945.png)