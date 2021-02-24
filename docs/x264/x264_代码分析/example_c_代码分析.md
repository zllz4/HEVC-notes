# example.c 代码分析

## 1 概述

`example.c` 提供了调用 x264 函数实现基本编码流程的框架，其主要分为两个部分，分别是**初始化部分**以及**编码/输出部分**。在初始化部分中，x264 **设置编码参数**，**为图片申请空间**，最后**初始化编码器**，在编码/输出部分中，`example.c` **交替进行编码部分与输出部分的操作**，每次读入一帧图片，然后执行编码，输出编码结果，如此循环直到视频编码完成。

## 2 初始化部分

### 2.1 结构体介绍

首先需要介绍以下结构体，这些结构体在 `example.c` 的开头被定义

```c
x264_param_t param;
x264_picture_t pic;
x264_picture_t pic_out;
x264_t *h;
x264_nal_t *nal;
```

对结构体的介绍如下：

- `x264_param_t` 是一个用于**存储输入参数**的结构体，通过修改输入参数，可以改变编码器的工作配置。x264 支持的输入参数可以使用 `x264.exe --help` 来查看（注意 `example.c` 编译出来的 exe 是不支持在调用时输入这些参数的），其分为以下几个类别
    - **预设值（Presents）**：选择预先设定好的参数模板集合，由于 x264 的参数设置十分复杂，所以提供了预设的模板用于各种情况，Presents 一共分为三类，分别为：
        - present：用于选择压缩质量和编码速度之间的 trade off，一共有 ultrafast/superfast/veryfast/faster/fast/medium/slow/slower/veryslow/placebo 这些选项，越 fast 的压缩质量（包括压缩后码率与重建质量）越低，越 slow 的压缩质量越高，其中 placebo 经[此网站](https://magiclen.org/x264-preset/)测试耗时相比 veryslow 有几倍提升但是质量几乎没有增长，所以一般不选，其它情况下是在可容忍范围内选择最慢的 present
        - tune：依据某一特定的视频类型修改编码参数增强编码效果，有下面这几种选项（图截自[此 csdn 博客](https://blog.csdn.net/NB_vol_1/article/details/78363559)）

            ![example_c_代码分析_6319442944](markdown_images/example_c_%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90_6319442944.png)

            还有一个 touhou 类型，直译为东方，~~可能是用于中国武打片或者印度歌舞片~~**没错这个类型的唯一目的就是[为了增强东方 Project 的游戏效果](https://www.reddit.com/r/touhou/comments/2vv6bh/til_a_parameter_in_the_x264_video_codec_was/)**  🤣

        - profile：限制输出视频流满足某个 profile 使其能够在能够解码对应 profile 的解码器中被解码，以此保证输出视频流的兼容性，profile 的选项有 baseline/main/high/high10/high422/high444。若要设置 profile，需在最后设置，以防其参数被覆盖。
    - **帧类型选项（Frame-type options）**：与帧类型决策相关的参数，控制编码器对当前帧属于 IDR/I 帧还是 P 帧还是 B 帧的选择，一般编码器每经过一定间隔或者发现场景转换时会编码一个 IDR 帧，而 B 帧和 P 帧则是根据某个决策算法来确定，这其中的具体过程会受到帧类型选项参数的控制
    - **码率控制（Ratecontrol）**：与码率控制相关的参数，在 x264 中有三种码率控制的方法，一为指定 qp（CQP），通过给定视频编码时的量化参数控制码率，二是指定 bitrate（CBR/ABR），通过设定视频编码后需要保持的（平均）码率大小来直接控制码率，三是指定 crf（CRF），通过指定视频编码后的需要保持的质量来控制码率，见[此网站](https://blog.shengbin.me/posts/x264-rate-control)
    - **输入/输出（Input/Output）**：指定输入和输出的文件格式，包括指定输入文件的色彩空间、分辨率，编码起始帧，总编码帧数和输出文件的文件名，格式，帧率，色彩空间等
    - **滤镜（Filtering）**：用于设置滤镜在**编码前**处理视频

    以上这些输入参数经过处理后送至 `x264_param_t` 进行存储。[此 wiki](https://www.nmm-hd.org/d/index.php?title=X264%E8%A8%AD%E5%AE%9A&variant=zh) 对 x264 的输入参数有比较详细的介绍，[这个 csdn 博客](https://blog.csdn.net/NB_vol_1/article/details/78362825)对 `x264_param_t` 中的各个成员有着比较详细的介绍。

- `x264_picture_t` 是用来**存储输入和重建的视频图像**的结构体，其中 `pic` 存储输入的一帧视频，`pic_out` 存储重建的一帧视频。在 `x264_picture_t` 的成员中有一个 `x264_image_t` 结构体（名为 `img`），这个 `x264_image_t` 的成员里有一个名为 `plane` 的指针数组，这个指针数组的每个成员都是一个 `uint8` 指针，**分别指向图像的每个颜色分量的存储空间**，因此，对于常用的 YUV422 格式来说，`pic.img.plane[0]` 为图像 Y 分量数据的存储空间首地址，`pic.img.plane[1]` 为图像 U 分量数据的存储空间首地址，`pic.img.plane[2]` 为图像 V 分量数据的存储空间首地址。
- `x264_t` 是用来**存储编码器状态**的结构体，从某种意义上来说，它也可以视为**编码器本身**，或者**编码器的句柄**，x264 中所有与编码器相关的函数都要用到这个结构体，所有编码过程中需要全局性保存（或者缓存）的参数也基本都被塞到了这个结构体上，包括已经编码的宏块缓存，当前的参考帧列表，当前编码的帧序号，当前编码的宏块位置，当前已编码数据的输出码流等等，前面提到的输入参数 `x264_param_t` 结构体在初始化编码器时也将被塞到 `x264_t` 结构体里面作为一个成员（名为 `param`）存储。基于这个结构体定义的指针变量一般被命名为 `h`。
- `x264_nal_t` 是用来**存储编码输出码流**的结构体，在编码结束时，编码函数会将 `h` 中存储的编码结果转移到 `x264_nal_t*` 类型的变量 `nal` 上，包括 NAL 单元类型，参考优先级和最终的编码码流等数据，其中最重要的编码码流数据被存储在这一结构体的 `p_payload` 成员中，这个成员是一个 `uint8` 类型的指针，指向码流的首地址。

### 2.2 编码参数设置

编码参数设置的主要目的就是设置 `x264_param_t` 结构体类型的变量 `param` 的初始值。由于 `example.c` 并不支持在调用时输入图片长宽以外的参数，因此编码参数主要是在程序内部设定。在 `example.c` 中编码参数设置的相关代码如下

```c
//Get default params for preset/tunnig
//第一步，设置 preset 和 tune 模板
if(x264_param_default_preset(&param, "medium", NULL) < 0)
    goto fail;

//Configure non-default params
//第二步，参数手动赋值
param.i_csp = X264_CSP_I420;
param.i_width = width;
param.i_height = height;
param.b_vfr_input = 0;
param.b_repeat_headers = 1;
param.b_annexb = 1;

//Apply profile restrictions.
//第三步，设置 profile 约束
if(x264_param_apply_profile(&param, "high") < 0)
    goto fail;
```

第一步调用 `x264_param_default_preset` 函数使用 **Presents** 中的 preset 和 tune 两个类型的模板来设置参数，`x264_param_default_preset` 函数的调用关系如下

1. 调用 `x264_param_default` 函数设置所有默认参数
2. 调用 `param_apply_preset` 函数按照传入的 preset 模板修改默认参数，其中 "medium" 是 ”不修改“，这是由于 `x264_param_default` 设计的默认配置就是属于 medium 类型的 preset
3. 调用 `param_apply_tune` 函数设置 tune 模板，NULL 也是不设置。

第二步手动赋值一些模板没有涉及到的参数，其中前缀 `i` 指 `int` 类型，前缀 `b` 指 `bool` 类型，`i_csp` 是色彩空间，`i_width` 和 `i_height` 是图像长宽（这个是输入参数），`b_vfr_input` 标志是否允许可变帧率，1 是允许（默认值）0 是不允许，`b_repeat_headers` 标志是否在发送每个 IDR 帧前发一遍 SPS 和 PPS，`b_annexb` 标志是否使用 AnnexB 的码流封装形式（关于 AnnexB 的介绍见[此 csdn 博客](https://blog.csdn.net/yue_huang/article/details/75126155)）

第三步调用 `x264_param_apply_profile` 函数使用 high profile 来约束编码器参数，完成参数设置

### 2.3 图像空间申请

之前提到 `pic.img.plane` 这一指针数组指向图像的三个颜色分量的存储空间，但是在 `x264_picture_t` 这个结构体建立时，这个存储空间本身是不存在的，因此需要有这一步来申请图像的存储空间。申请函数如下

```c
if(x264_picture_alloc(&pic, param.i_csp, param.i_width, param.i_height) < 0)
    goto fail;
```

输入参数是图像的长宽和色彩空间，`x264_picture_alloc` 函数的工作是首先对输入的变量 `pic` 指向的 `x264_picture_t` 结构体进行初始化（对一些参数赋予初值），之后根据色彩空间 `i_csp` 和长宽算出图片每一个颜色分量（比如 YUV 分量）数据所需要的空间大小，得到图片数据的总大小 `frame_size`，然后调用 `x264_malloc` 函数申请 `frame_size` 大小的空间，最后将得到的空间划分分配给每个颜色分量。

在这步操作之后，`pic->img.plane[i]` 指向的空间才真正具有意义。

### 2.4 初始化编码器

初始化编码器的目的是根据输入参数变量 `param` 初始化编码器状态变量 `h` ，以便之后使用 `h` 进行编码操作，这一步骤通过调用 `x264_encoder_open` 函数实现

```c
h = x264_encoder_open(&param);
if(!h)
    goto fail;
```

`x264_encoder_open` 函数将在之后介绍，其重要流程是新建一个 `x264_t` 类型的结构体，为这一结构体分配空间然后将 `param` 中包含包含的参数复制过去，之后则是对该 `x264_t` 结构体的其它一些参数进行初始化，这里比较重要的是在初始化过程中程序会选择**具体执行编码中预测、DCT 变换、量化等操作使用的函数**，如果系统支持某一特定的指令集，那么程序会选择对应指令集的汇编版本函数进行加速，如果没有则选择默认的 c 语言版本函数。在初始化结束后，`x264_encoder_open` 会输出一些控制信息，包括档次、等级、色度亚采样格式和比特深度，就是前文 [x264 使用] 章节中展示的编码输出的这一行

```c
x264 [info]: profile High, level 1.3, 4:2:0, 8-bit
```

## 3 图像编码与输出

`example.c` 的图像编码/输出部分涵盖在这个 for 循环中

```c
for(;;i_frame++)
{
    /* ------------------ 编码部分 ------------------- */
    // 读取图片数据
    if(fread(pic.img.plane[0], 1, luma_size, fp_src)!=luma_size)
        break;
    if(fread(pic.img.plane[1], 1, chroma_size, fp_src)!=chroma_size)
        break;
    if(fread(pic.img.plane[2], 1, chroma_size, fp_src)!=chroma_size)
        break;

    pic.i_pts = i_frame;
    // 进行编码
    i_frame_size = x264_encoder_encode(h, &nal, &i_nal, &pic, &pic_out);
    /* ------------------ 输出部分 ------------------- */
    if(i_frame_size < 0)
        goto fail;
    else if(i_frame_size)
    {
        // 输出写入文件
        if(!fwrite(nal->p_payload, i_frame_size, 1, fp_dst))
            goto fail;
    }
}

/* ------------------ 输出延迟帧 ------------------- */
while(x264_encoder_delayed_frames(h))
{
    i_frame_size = x264_encoder_encode(h, &nal,&i_nal, NULL, &pic_out);
    if(i_frame_size < 0)
        goto fail;
    else if(i_frame_size)
    {
        if(!fwrite(nal->p_payload, i_frame_size, 1, fp_dst))
            goto fail;
    }
}
```

首先使用 `fread` 读取图片至 YUV 分量的存储空间中，之后使用 `x264_encoder_encode` 进行编码，`x264_encoder_encode` 的功能是编码一帧的图像，其输入是编码器状态参数 `h`，输入图像 `pic`，输出是编码码流 `nal`（还有一个 `i_nal` 可能是指图像编码形成的 NAL 单元数量）和重建图像 `pic_out`。

`x264_encoder_encode` 函数也将在之后进行介绍，其主要流程是做各种编码前的准备工作，然后调用 `slices_write` 函数进行帧编码。在编码前的准备工作中，`x264_encoder_encode` 函数首先将输入图片数据复制进一个 `x264_frame_t` 类型的结构体 `fenc` 中，这个结构体可以视为 `x264_picture_t` 的加强版，在 YUV 数据之外也增加了许多与**该帧有关的编码相关信息**的存储，比如这个图片的类型（I/B/P），它的参考帧关系，它的编码 QP，编码序号，还有一些分块和环路滤波相关参数等等，由于多了很多参数，所以 `x264_encoder_encode` 函数后面大段大段代码都是在给这些参数初始化，初始化好之后把 `fenc` 推送到**帧类型决策等待序列**中，这个序列在代码中为 `h->lookahead->next`，然后从**已经决策完毕帧类型的待编码序列**中取出一帧，进行编码，这个序列在代码中为 `h->frames.current`，这一取帧过程需要进行如下判断：

- 如果待编码序列中有帧，那么直接从中取一帧
- 如果待编码序列为空（所有帧被取完了），那么对帧类型决策等待序列中的若干帧执行帧类型决策（决定其是 I/P/B 帧中的哪一种），然后将决策好的帧**按照编码顺序**放入待编码序列中，再从待编码序列中取出一帧

这一步实现了**输入顺序到编码顺序的转换**。

在获取到当前要编码的帧之后，`x264_encoder_encode` 会继续进行准备工作，首先，其通过 `reference_update` 函数更新参考帧列表（即解码图像缓存 DPB），如果当前帧是关键帧（keyframe，也就是 IDR 帧），那么其会调用 `reference_reset` 函数清空参考帧列表。在参考帧列表更新完毕后，`x264_encoder_encode` 会调用 `reference_build_list` 函数根据当前参考帧列表生成当前帧的参考序列 ref list 0 和 ref list 1。之后则进行码流的初始化，AUD（access unit 的分割符）以及 SPS、PPS 和 SEI NAL 单元的写入。

在四个 NAL 单元写完之后， `x264_encoder_encode` 会调用 `slices_write` 函数开始真正的编码，这个函数将图片帧分成一个个 slice，然后对每个 slice 调用 `slice_write` 函数进行编码，`slice_write` 函数则遍历输入的 slice 的每一个宏块，先调用 `x264_macroblock_analyse` 函数对宏块进行分析，通过对宏块进行不同划分的帧内预测和帧间预测，确定其最佳的预测模式（帧内还是帧间）、划分方式（帧内可以有 9 种，帧间可以有 8 种）和运动向量（当最佳模式为帧间模式），再调用 `x264_macroblock_encode` 函数对宏块进行编码，对残差进行 dct 变换、量化、反量化、反变换，得到量化后的 dct 系数以及重建宏块，最后调用 CAVLC 或者 CABAC 的熵编码函数进行熵编码，得到编码码流。

在 `slices_write` 函数运行结束后， `x264_encoder_encode` 将会调用 `encoder_frame_end` 函数结束当前帧的编码，此函数会将编码结果转移到作为输出的 `x264_nal_t` 类型的变量 `nal` 中，同时将 `fdec`（与 `fenc` 对应的重建帧）的数据转移到同样作为输出的重建图像 `pic_out` 中。

在编码完成后，我们需要通过 `fwrite` 将输出码流 `nal->p_payload` 写入文件中。`x264_encoder_encode` 函数的返回值 `i_frame_size` 对应了输出码流的长度，在某些设置下（主要的影响因素是多线程和 B 帧），从输入到编码输出的过程存在延迟，因此会出现以下三种情况（这三种情况在下一章 [x264 的输入顺序、编码顺序、输出顺序与延迟] 有进一步介绍）：

1. **某一帧图像数据输入，`x264_encoder_encode` 函数没有产生编码码流输出**（`i_frame_size` 为零）：这种情况往往会出现在**编码的开头**，编码器会先吞掉若干帧用于多线程 / lookahead 等一些目前还不太搞的清楚的操作，在这种情况下，程序不需要将任何数据写入文件，直接继续进行下一帧的编码
2. **某一帧图像数据输入，`x264_encoder_encode` 函数产生了一帧的编码输出**（`i_frame_size` 不为零）：这种情况往往出现在**编码的中间过程**，此时编码器输入一帧，输出一帧，其表现与我们的正常认知相同，但是需注意，输出的一帧与输入的一帧并不一定是同一帧，这里存在从输入顺序到编码顺序的转换，在这种情况下我们需要做的处理就是检测 `i_frame_size`，当发现其不为零则将输出码流写入到文件中，也就是之前代码的这一段

    ```c
    else if(i_frame_size)
    {
        // 输出写入文件
        if(!fwrite(nal->p_payload, i_frame_size, 1, fp_dst))
            goto fail;
    }
    ```

3. **没有编码图像数据输入，`x264_encoder_encode` 函数产生了一帧的编码输出**（`i_frame_size` 不为零）：这种情况往往出现在**编码的结尾**，此时所有的视频帧已经输入给编码器了，但是由于前面的第一种情况的存在，编码器并没有输出所有视频帧的编码结果，因此需要继续给编码器喂空白的输入，让它继续输出，直到所有的编码视频帧输出完毕。编码器是否存在被延迟的输出可以用 `x264_encoder_delayed_frames` 函数检测，因此在这种情况下我们需要不断使用空白输入调用编码函数获取输出直到此检测函数输出为零，也就是之前代码的这一段

    ```c
    /* ------------------ 输出延迟帧 ------------------- */
    while(x264_encoder_delayed_frames(h)) // 检测是否有延迟帧
    {
        // 如果有延迟帧，以空白输入调用编码函数获取延迟帧
        i_frame_size = x264_encoder_encode(h, &nal,&i_nal, NULL, &pic_out);
        if(i_frame_size < 0)
            goto fail;
        else if(i_frame_size)
        {
            // 输出写入文件
            if(!fwrite(nal->p_payload, i_frame_size, 1, fp_dst))
                goto fail;
        }
    }
    ```

最后，对于重建图像，[此网站](https://blog.shengbin.me/posts/output-picture-in-x264-encoder-encode)给出了利用 `pic_out` 输出编码后重建视频的代码，不过未经测试。