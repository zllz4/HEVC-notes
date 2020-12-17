# HM 编译测试

## 1 概述

HM 全称 HEVC Test Model，为 **HEVC 官方提供的编解码器源码**，其由 `c++` 编写，目前（2020 年）的最新版本为 16.22。由于 HM 16.20 往后似乎由 vs 改为了 cmake 进行 build，以下采用 vs 进行操作的方法仅最高适用于 HM 16.20

## 2 编译测试流程

HM 编辑测试流程如下

1. 从[此网站](https://vcgit.hhi.fraunhofer.de/jct-vc/HM)下载 HM 16.20 版本（HM 16.20 版本之后的版本没有 sln 文件），按下图方式选择版本

    ![HM_编译测试_82240](markdown_images/HM_%E7%BC%96%E8%AF%91%E6%B5%8B%E8%AF%95_82240.png)

2. 打开某个版本的 sln（位于 `HM-HM-16.20\build`），vs 会默认提示你是否要升级，选择升级（重定向）到你的 vs 的工具集版本

    > 默认情况下你下载好的源代码文件夹名称应该是 `HM-HM-16.20`

3. **编译编码器**，选择 `TAppEncoder`，设为启动项目，按 F5 编译

    > vs 里面一个解决方案可以有多个项目，可以设置其中的某一个项目为 ”启动项目“

    图示如下

    ![HM_编译测试_32704](markdown_images/HM_%E7%BC%96%E8%AF%91%E6%B5%8B%E8%AF%95_32704.png)

4. **编译解码器**，选择 `TAppDecoder`，设为启动项目，按 F5 编译，此时可以在 `HM-HM-16.20\bin\vc2015\Win32\Debug` 目录下找到 `TAppEncoder.exe` 和 `TAppDecoder.exe`
5. 从[此网站](https://blog.csdn.net/abcSunl/article/details/53841953)中下载视频测试文件，**CTC**（Common Test Condition）中定义的视频测试序列如下

    ![HM_编译测试_11008](markdown_images/HM_%E7%BC%96%E8%AF%91%E6%B5%8B%E8%AF%95_11008.png)

    ![HM_编译测试_31008](markdown_images/HM_%E7%BC%96%E8%AF%91%E6%B5%8B%E8%AF%95_31008.png)

6. 5 步骤下载下来的视频是 `.yuv` 格式的，从[此网站](https://github.com/IENT/YUView/releases)下载能够查看 `.yuv` 格式视频的播放器，下载完成后试验一下能否打开，正常结果如下

    ![HM_编译测试_61952](markdown_images/HM_%E7%BC%96%E8%AF%91%E6%B5%8B%E8%AF%95_61952.png)

    按一下空格开始播放，再按一下暂停，这个软件可以查看视频文件的**实际帧数**，有时候视频文件的实际帧数会比之前表格上写的多一帧，多出来那个是黑底白字的版权说明

7. 将 `HM-HM-16.20\cfg\encoder_intra_main.cfg` 以及 `HM-HM-16.20\cfg\per-sequence\BasketballDrill.cfg` 复制到 `HM-HM-16.20\bin\vc2015\Win32\Debug` 目录下，**前者保持默认，将后者按照如下规则修改**

    ```bash
    #======== File I/O ===============
    InputFile                     : /path/to/yuv # 要修改，YUV 文件位置
    InputBitDepth                 : 8           # 输入视频比特深度，注意 A Class 里面的 Nebuta 和 SteamLocomotive 是 10 bit 要修改
    InputChromaFormat             : 420         # Ratio of luminance to chrominance samples
    FrameRate                     : 50          # 要修改，每秒播放多少帧，见上表
    FrameSkip                     : 0           # Number of frames to be skipped in input
    SourceWidth                   : 352         # 要修改，视频宽度，见上表
    SourceHeight                  : 288         # 要修改，视频长度，见上表
    FramesToBeEncoded             : 2000         # 要修改，想要编码的帧数（最大为视频帧数），见上表

    Level                         : 3.1
    ```

8. 在 bin 文件夹的地址栏中输入 cmd 打开终端输入 `TAppEncoder.exe -c encoder_intra_main.cfg -c BasketballDrill.cfg` 开始编码，编码结束后可以得到 `rec.yuv` 以及 `str.bin` 文件，前者是在编码过程中重建输入的文件，后者是视频的最终编码结果，两者的大小之比就是压缩率
9. 使用 **potplayer** 可以观看 `.bin` 文件，检查是否压缩后能够正常播放，此时按 tab 可以输出视频详细信息

    potplayer 下载地址推荐[官网](https://potplayer.daum.net/)

    如果嫌官网太慢，可以通过这个[蓝奏云链接](https://wwe.lanzous.com/iKsBSjgdawf)下载

    > 别问我为啥是 p0tplayer，potplayer 好像是蓝奏云的敏感词我也不知道为啥

10. 可以将上文中的 `encoder_intra_main.cfg` 更换为 `cfg` 文件夹的以下配置，提供不同的编码功能，使用方法同上，把配置复制过去然后 `-c` 引用
    - `encoder_intra_main.cfg`：纯 I 帧编码，8/10 bit 输入，**全部 8 bit 输出**，使用 potplayer 播放时会发现可以拖动进度条到任意位置（因为**每一帧都可以作为随机切入点**），压缩率**低**，其编码输出帧序列的结构示意图如下

        ![HM_编译测试_68608](markdown_images/HM_%E7%BC%96%E8%AF%91%E6%B5%8B%E8%AF%95_68608.png)

    - `encoder_lowdelay.cfg/encoder_lowdelay_P.cfg`： 第一个 I 帧之后全是 B/P 帧，B/P 帧**只参考播放顺序在其之前的帧**而不参考播放顺序在其之后的帧，因此可以达到**低延时**（lowdelay），使用 potplayer 播放时会发现无法拖动进度条（因为**不存在随机切入点**），压缩率**高**，其编码输出帧序列的结构示意图如下

        ![HM_编译测试_63744](markdown_images/HM_%E7%BC%96%E8%AF%91%E6%B5%8B%E8%AF%95_63744.png)

        > low_delay_P 相比 low_delay 而言编解码复杂度更低，因为其只需要参考前面一个帧（low_delay 要参考前面两个帧），然而压缩效果略差，不过就实际效果而言似乎差不多

    - `encoder_randomaccess.cfg`：每 16 帧一组，每组以 I 帧开头，后面是 B 帧，**B 帧的参考结构具有层次性**，上层 B 帧参考下层 B 帧，**间隔性插入 I 帧**来阻止误差传播以及作为随机切入点，具有最高的压缩率以及**最长的延时**（由于 RA 中存在**后向参考**，导致**解码顺序不等于播放顺序**，播放时需要等待播放顺序在当前帧之后的帧解码才能播放当前帧，**造成延时增大**，这也是前面只参考前面帧的配置方式被称为“低延时”的原因），使用 potplayer 播放时会发现可以在某些位置拖动进度条（因为**存在部分帧作为随机切入点**），压缩率**高**，其编码输出帧序列的结构示意图如下

        ![HM_编译测试_44832](markdown_images/HM_%E7%BC%96%E8%AF%91%E6%B5%8B%E8%AF%95_44832.png)

    - `encoder_xxx_main10.cfg`：xxx 为 `intra` 或 `lowdelay` 等，功能等同于 `encoder_xxx.cfg` 的功能，只不过**输入输出情况不同**，此时为 8/10 bit 输入，**全部 10 bit 输出**
11. 在 vs 中可以调整生成的 exe 属于 debug 环境还是 release 环境，之前默认生成的是 debug 环境，事实上 release 环境生成的 exe 文件编码速度比 debug 生成的 exe 文件快的多