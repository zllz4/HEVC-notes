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

            ![example_c_代码分析_42944](markdown_images/example_c_%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90_42944.png)

            还有一个 touhou 类型，直译为东方，~~可能是用于中国武打片或者印度歌舞片~~**没错这个类型的唯一目的就是[为了增强东方 Project 的游戏效果](https://www.reddit.com/r/touhou/comments/2vv6bh/til_a_parameter_in_the_x264_video_codec_was/)**  🤣

        - profile：限制输出视频流满足某个 profile 使其能够在能够解码对应 profile 的解码器中被解码，以此保证输出视频流的兼容性，profile 的选项有 baseline/main/high/high10/high422/high444。若要设置 profile，需在最后设置，以防其参数被覆盖。
    - **帧类型选项（Frame-type options）**：与帧类型决策相关的参数，控制编码器对当前帧属于 IDR/I 帧还是 P 帧还是 B 帧的选择，一般编码器每经过一定间隔或者发现场景转换时会编码一个 IDR 帧，而 B 帧和 P 帧则是根据某个决策算法来确定，这其中的具体过程会受到帧类型选项参数的控制
    - **码率控制（Ratecontrol）**：与码率控制相关的参数，在 x264 中有三种码率控制的方法，一为指定 qp（CQP），通过给定视频编码时的量化参数控制码率，二是指定 bitrate（CBR/ABR），通过设定视频编码后需要保持的（平均）码率大小来直接控制码率，三是指定 crf（CRF），通过指定视频编码后的需要保持的质量来控制码率，见[此网站](https://blog.shengbin.me/posts/x264-rate-control)
    - **输入/输出（Input/Output）**：指定输入和输出的文件格式，包括指定输入文件的色彩空间、分辨率，编码起始帧，总编码帧数和输出文件的文件名，格式，帧率，色彩空间等
    - **滤镜（Filtering）**：用于设置滤镜在**编码前**处理视频

    以上这些输入参数经过处理后送至 `x264_param_t` 进行存储。[这个 csdn 博客](https://blog.csdn.net/yue_huang/article/details/79309696)对 x264 的输入参数有比较详细的介绍，[这个 csdn 博客](https://blog.csdn.net/NB_vol_1/article/details/78362825)对 `x264_param_t` 中的各个成员有着比较详细的介绍。

- `x264_picture_t` 是用来**存储输入和重建的视频图像**的结构体，其中 `pic` 存储输入的一帧视频，`pic_out` 存储重建的一帧视频。在 `x264_picture_t` 的成员中有一个 `x264_image_t` 结构体（名为 `img`），这个 `x264_image_t` 的成员里有一个名为 `plane` 的指针数组，这个指针数组的每个成员都是一个 `uint8` 指针，**分别指向图像的每个颜色分量的存储空间**，因此，对于常用的 YUV422 格式来说，`pic.img.plane[0]` 为图像 Y 分量数据的存储空间首地址，`pic.img.plane[1]` 为图像 U 分量数据的存储空间首地址，`pic.img.plane[2]` 为图像 V 分量数据的存储空间首地址。
- `x264_t` 是用来**存储编码器状态**的结构体，从某种意义上来说，它也可以视为**编码器本身**，或者**编码器的句柄**，x264 中所有与编码器相关的函数都要用到这个结构体，所有编码过程中需要全局性保存（或者缓存）的参数也基本都被塞到了这个结构体上，包括已经编码的宏块缓存，当前的参考帧列表，当前编码的帧序号，当前编码的宏块位置，当前已编码数据的输出码流等等，前面提到的输入参数 `x264_param_t` 结构体在初始化编码器时也将被塞到 `x264_t` 结构体里面作为一个成员（名为 `param`）存储。基于这个结构体定义的指针变量一般被命名为 `h`。
- `x264_nal_t` 是用来**存储编码输出码流**的结构体，在编码结束时，编码函数会将 `h` 中存储的编码结果转移到 `x264_nal_t*` 类型的变量 `nal` 上，包括 NAL 单元类型，参考优先级和最终的编码码流等数据，其中最重要的编码码流数据被存储在这一结构体的 `p_payload` 成员中，这个成员是一个 `uint8` 类型的指针，指向码流的首地址。

### 2.2 编码参数设置

编码参数设置的主要目的就是设置 `x264_param_t` 结构体类型的变量 `param` 的初始值。由于 `example.c` 并不支持在调用时输入图片长宽以外的参数，因此编码参数主要是在程序内部设定。在 `example.c` 中编码参数设置的相关代码如下

```c
//Get default params for preset/tunnig
if(x264_param_default_preset(&param, "medium", NULL) < 0)
    goto fail;

//Configure non-default params
param.i_csp = X264_CSP_I420;
param.i_width = width;
param.i_height = height;
param.b_vfr_input = 0;
param.b_repeat_headers = 1;
param.b_annexb = 1;

//Apply profile restrictions.
if(x264_param_apply_profile(&param, "high") < 0)
    goto fail;
```

第一步调用 `x264_param_default_preset` 函数使用 Presents 中的 preset 和 tune 两个类型的模板来设置参数，对于 present，选择 "medium" 类型的模板，对于 tune，选择 NULL 即不使用。

第二步手动赋值一些模板没有涉及到的参数，其中 `i_csp` 是色彩空间（i 指 int 类型），`i_width` 和 `i_height` 是图像长宽（这个是输入参数），`b_vfr_input` 标志是否允许可变帧率（b 指 `bool` 类型），1 是允许（默认值）0 是不允许，`b_repeat_headers` 标志是否在发送每个 IDR 帧前发一遍 SPS 和 PPS，`b_annexb` 标志是否使用 AnnexB 的码流封装形式（关于 AnnexB 的介绍见[此 csdn 博客](https://blog.csdn.net/yue_huang/article/details/75126155)）

第三步调用 `x264_param_apply_profile` 函数使用 high profile 来约束编码器参数，完成参数设置

### 2.3 图像空间申请

之前提到 `pic.img.plane` 这一指针数组指向图像的三个颜色分量的存储空间，但是在 `x264_picture_t` 这个结构体建立时，这个存储空间本身是不存在的，因此需要有这一步来申请图像的存储空间。申请函数如下

```c
if(x264_picture_alloc(&pic, param.i_csp, param.i_width, param.i_height) < 0)
    goto fail;
```

输入参数是图像的长宽和色彩空间，根据此可以算出一帧图像需要消耗的存储空间大小，之后调用 `malloc` 函数完成空间申请

### 2.4 初始化编码器

初始化编码器的目的是根据输入参数变量 `param` 初始化编码器状态变量 `h` ，以便之后使用 `h` 进行编码操作，这一步骤通过调用 `x264_encoder_open` 函数实现

```c
h = x264_encoder_open(&param);
if(!h)
    goto fail;
```

这个 `x264_encoder_open` 函数中调用了较多的初始化函数，具体分析可以见[雷神博客](https://blog.csdn.net/leixiaohua1020/article/details/45644367)（我还没太看懂，看懂就写）

## 3 图像编码与输出

example.c 的图像编码/输出部分涵盖在这个 for 循环中

```c
for(;;i_frame++)
{
		/* ------------------ 编码部分 ------------------- */
    //Read input frame
    if(fread(pic.img.plane[0], 1, luma_size, fp_src)!=luma_size)
        break;
    if(fread(pic.img.plane[1], 1, chroma_size, fp_src)!=chroma_size)
        break;
    if(fread(pic.img.plane[2], 1, chroma_size, fp_src)!=chroma_size)
        break;

    pic.i_pts = i_frame;
    i_frame_size = x264_encoder_encode(h, &nal, &i_nal, &pic, &pic_out);
		/* ------------------ 输出部分 ------------------- */
    if(i_frame_size < 0)
        goto fail;
    else if(i_frame_size)
    {
        if(!fwrite(nal->p_payload, i_frame_size, 1, fp_dst))
            goto fail;
    }
}
```

首先使用 `fread` 读取图片至 YUV 分量的存储空间中，之后使用 `x264_encoder_encode` 进行编码（这个函数又是各种看不懂），`x264_encoder_encode` 的功能是编码一帧的图像，其输入是编码器状态参数 `h`，输入图像 `pic`，输出是编码码流 `nal`（还有一个 `i_nal` 可能是指图像编码形成的 NAL 单元数量（存疑））和重建图像 `pic_out`。

`x264_encoder_encode` 函数本身并没有涵盖具体的编码行为，其主要做的是一些编码前的准备工作，包括将输入图片数据复制进一个 `x264_frame_t` 类型的结构体 `fenc` 中，这个结构体可以视为 `x264_picture_t` 的加强版，在 YUV 数据之外也增加了许多与**该帧有关的编码相关信息**的存储，比如这个图片的类型（I/B/P），它的参考帧关系，它的编码 QP，编码序号，还有一些分块和环路滤波相关参数等等，由于多了很多参数，所以 `x264_encoder_encode` 函数后面大段大段代码都是在给这些参数初始化，初始化好之后把 `fenc` 推送到**帧类型决策等待序列**中，这个序列在代码中为 `h->lookahead->next`，然后从**已经决策完毕帧类型的待编码序列**中取出一帧，进行编码，这个序列在代码中为 `h->frames.current`。

这里需要解释一下这个操作，在编码过程中，由于帧间参考关系或是其它一些原因，图像的编码顺序和播放顺序可能不同，这就会造成时延，比如当前输入的帧是 A，它要参考之后输入的下一帧 B，那么当前 A 就不能编码，等到下一帧 B 帧到来时 B 先编码，然后 A 后编码，此时假设 B 帧的编码是实时的，那么 A B 两帧输入需要两个时间单位，但是输出需要三个时间单位，此时就有一个时间单位的延时。延时会造成等待，在第三个时间段假设有个 C 图像输入，那么在 x264 的编码流程中， C 图像就需要被送到**帧类型决策等待序列**，然后我们从**已经决策完毕帧类型的待编码序列**中取出一张图像，即 A 图像，对 A 图像进行编码。在第四个时间段 D 图像输入，此时编码器先将 D 图像也加入**帧类型决策等待序列**，然后检测**已经决策完毕帧类型的待编码序列**，发现里面为空，那么便开始对**帧类型决策等待序列**中的图片进行帧类型决策，发现 C 依赖 D（这里是猜想，不清楚决策帧类型时是否会决策依赖关系），因此 D 放到待编码序列首位，C 放到后位，然后从待编码序列中取出一帧 D 进行编码，以此类推，在 `example.c` 后面还有一段代码输出 delayed frames（如下），这些 delayed frames 的存在可能也是部分由于这个原因

```c
//Flush delayed frames
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

在获取到当前要编码的帧之后，`x264_encoder_encode` 会继续进行准备工作，首先，其通过 `reference_update` 函数更新参考帧列表（即解码图像缓存 DPB），如果当前帧是关键帧（keyframe，也就是 IDR 帧），那么其会调用 `reference_reset` 函数清空参考帧列表。在参考帧列表更新完毕后，`x264_encoder_encode` 会调用 `reference_build_list` 函数根据当前参考帧列表生成当前帧的参考序列 ref list 0 和 ref list 1。之后进行码流的初始化，AUD（access unit 的分割符）以及 SPS、PPS 和 SEI NAL 单元的写入，在四个 NAL 单元写完之后调用 `slices_write` 函数开始真正的编码，在 `slices_write` 函数中的 `slice_write` 函数负责执行具体的编码行为，包括帧内帧间预测、变换量化和环路滤波等，这个 `slice_write` 函数的调用关系比较复杂，可以看[雷神的高清函数调用图](https://img-my.csdn.net/uploads/201505/06/1430897637_6272.jpg)。在上述编码结束后， `x264_encoder_encode` 将会调用 `encoder_frame_end` 函数结束编码，此函数会将编码结果转移到作为输出的 `x264_nal_t` 类型的变量 `nal` 中，同时将 `fdec`（与 `fenc` 对应的重建帧）的数据转移到同样作为输出的重建图像 `pic_out` 中。

在编码完成后，通过 `fwrite` 将输出码流 `nal->p_payload` 写入文件中。之所以只写入 `p_payload`，是因为根据 x264 官方给出的注释，`x264_nal_t` 虽然除了 `p_payload` 成员以外还有其它一些成员，比如表示 NAL 单元类型的 `i_type` 和表示 NAL 单元参考优先级的 `i_ref_idc`，但是这些成员实际上也是已经包含在 `p_payload` 里面的，在 `x264_nal_t` 里面把这些参数再重复一遍只是为了获取方便，因此没有必要把这些参数也一并写入。

对于重建图像，[此网站](https://blog.shengbin.me/posts/output-picture-in-x264-encoder-encode)给出了利用 `pic_out` 输出编码后重建视频的代码，不过未经测试。