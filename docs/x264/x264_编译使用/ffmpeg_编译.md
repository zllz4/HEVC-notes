# ffmpeg 编译

## 1 概述

本节主要介绍如何从源码编译 ffmpeg 作为 x264 的解码器（只使用其解码功能）

## 2 编译步骤

1. 从 [ffmpeg 官方网站](https://ffmpeg.org/download.html)下载源码
2. 打开 msys2，运行 `congfigure` 程序配置 `Makefile`

    ```bash
    ./configure \
      --prefix=./build \                # 输出文件地址
      --disable-everything \            # 禁止无关功能，减小文件体积
      --enable-protocol=file \          # 允许从本地读取/写入视频文件（编码/解码端）
      --enable-demuxer=h264 \           # 允许解除 h264 类型视频文件的封装（解码端）
      --enable-parser=h264 \            # 允许解析 h264 类型码流（解码端）
      --enable-decoder=h264 \           # 允许解码 h264 类型视频编码（解码端）
      --enable-encoder=rawvideo \       # 允许 rawvideo 类型编码（编码端）
      --enable-muxer=rawvideo \         # 允许 rawvideo 类型封装（编码端）
      --disable-optimizations           # 禁止优化，方便 debug
      --enable-debug \                  # 在编译指令中添加 -g 参数，以支持 debug
      --disable-asm \                   # 禁用汇编，用于 debug
      --disable-stripping \             # 防止断点被自动去掉，用于 debug
    ```

    关于 `protocol`，`demuxer` 等功能模块的说明可以见[此网站](https://juejin.cn/post/6844903694916386823)，由于这里 ffmpeg 只是用来解码 x264 编码好的视频并生成 `yuv` 文件，因此解码端只需要支持 `h264` 码流，编码和输出端只需要支持 `rawvideo`

    ffmpeg 支持的 `protocol` 列表和相关说明：[点此访问](https://ffmpeg.org/ffmpeg-protocols.html)

    ffmpeg 支持的 `muxer` 和 `demuxer` 列表和相关说明：[点此访问](https://ffmpeg.org/ffmpeg-formats.html)

    ffmpeg 支持的 `encoder` 和 `decoder` 列表和相关说明：[点此访问](https://ffmpeg.org/ffmpeg-codecs.html)

    运行上述指令时会好像卡住一样什么都没有输出持续很长一段时间，实际上程序是正常执行的，此时可以在 `ffbuild/config.log` 文件中查看 `configure` 程序的运行情况

3. 创建一个 `build` 文件夹，然后进行 `make`

    ```bash
    mkdir build
    make && make install
    ```

    如果嫌 `make` 慢可以使用 `make -j4` 进行多线程（这里是 4 线程）并行的 `make`

    完成后可以在 `build/bin` 文件夹中找到编译完成的 `ffmpeg.exe` 和 `ffprobe.exe`

4. 使用 `ffmpeg.exe` 解码 x264 编码码流

    假设待解码的码流是 `output.bin`，放在与 `ffmpeg.exe` 相同的文件夹

    ```bash
    ./ffmpeg.exe -i output.bin rec.yuv
    ```

    ffmpeg 输出如下

    ```bash
    ffmpeg version N-101405-g2570663 Copyright (c) 2000-2021 the FFmpeg developers
      built with gcc 10.2.0 (Rev5, Built by MSYS2 project)
      configuration: --prefix=./build --disable-everything --enable-protocol=file --enable-demuxer=h264 --enable-parser=h264 --enable-decoder=h264 --enable-encoder=rawvideo --enable-muxer=rawvideo --disable-optimizations
      libavutil      56. 67.100 / 56. 67.100
      libavcodec     58.129.100 / 58.129.100
      libavformat    58. 71.100 / 58. 71.100
      libavdevice    58. 12.100 / 58. 12.100
      libavfilter     7.109.100 /  7.109.100
      libswscale      5.  8.100 /  5.  8.100
      libswresample   3.  8.100 /  3.  8.100
    Input #0, h264, from 'C:/Users/admin/Desktop/x264/x264-work/x264_encode/video/output.bin':
      Duration: N/A, bitrate: N/A
      Stream #0:0: Video: h264 (High), yuv420p(progressive), 416x240, 50 fps, 50 tbr, 1200k tbn, 100 tbc
    Stream mapping:
      Stream #0:0 -> #0:0 (h264 (native) -> rawvideo (native))
    Press [q] to stop, [?] for help
    Output #0, rawvideo, to 'rec.yuv':
      Metadata:
        encoder         : Lavf58.71.100
      Stream #0:0: Video: rawvideo (I420 / 0x30323449), yuv420p(progressive), 416x240, q=2-31, 59904 kb/s, 50 fps, 50 tbn
        Metadata:
          encoder         : Lavc58.129.100 rawvideo
    frame=  502 fps=0.0 q=-0.0 Lsize=   73418kB time=00:00:10.06 bitrate=59784.9kbits/s dup=1 drop=0 speed=63.3x
    video:73418kB audio:0kB subtitle:0kB other streams:0kB global headers:0kB muxing overhead: 0.000000%
    ```

    解码后生成 `rec.yuv`

5. 如果需要详细输出每一帧的解码情况，可以在调用 `ffmpeg.exe` 时设置 loglevel

    ```bash
    ./build/bin/ffmpeg.exe -v trace -i C:/Users/admin/Desktop/x264/x264-work/x264_encode/video/output.bin rec.yuv
    ```

    loglevel 可以用 `-v` 或者 `-loglevel` 设定，具体等级见[此网站](https://www.jianshu.com/p/2be79f17e271)

6. 编译完成后可以按照前面 [x264 调试] 章节的内容进行 debug，根据网上说法调试需要使用 `ffmpeg_g.exe`，但是根据实际测试按照上面方法编译的 `ffmpeg.exe` 也是能打断点的

## 3 ffmpeg.exe 的函数路径

雷神的笔记：[点此访问](https://blog.csdn.net/leixiaohua1020/article/details/39760711)

入口：`main` in `ffmpeg.c`

`main` 调用：

- `show_banner`
- `ffmpeg_parse_options`
- `transcode`：编解码**主函数**
- `exit_program`

`transcode` 调用：

- `transcode_init`
    - `init_input_stream`
    - `init_output_stream_wrapper`
- `check_keyboard_interaction`：检查输入是否为 q，为 q 则退出
- `transcode_step`：被循环调用，处理一个 packet
- `print_report`

`transcode_step` 调用：

- `choose_output`
- `process_input`：**解码**一个 packet
- `reap_filters`：**编码**一个 packet

`process_input` 调用：

- `get_input_packet`：读入一个 packet
    - `av_read_frame`
- `process_input_packet`：解码读入的 packet

`process_input_packet` 调用：

- `decode_audio`：当输入为音频时调用，解码输入的音频 packet
- `decode_video`：当输入为视频时调用，解码输入的视频 packet
- `do_streamcopy`

`decode_video` 调用：

- `decode`
    - `avcodec_send_packet`："feed input to decoder"
        - `av_bsf_send_packet`：将输入的 packet 送到 `AVBSFContext->AVPacket` 中
        - `decode_receive_frame_internal`：解码输入的 packet（这是第几层套娃了？？？）
    - `avcodec_receive_frame`："receive decoded frames after each packet"
        - `decode_receive_frame_internal`

    > 这两个新 API 代替了原有的 `avcodec_decode_video2` 和 `avcodec_decode_audio4` 函数

    关于这两个函数的介绍可见[此网站](https://regenttsui.github.io/%E7%BC%96%E8%A7%A3%E7%A0%81%E6%96%B0API.html)

`decode_receive_frame_internal` 调用：

- `avctx->codec->receive_frame`：解码函数，不同解码器不同
- `decode_simple_receive_frame`：当解码器没有定义 `receive_frame` 函数时调用这个
    - `decode_simple_internal`
        - `avctx->codec->decode`：**真正的解码函数**，不同解码器不同（估计之前的 `avctx->codec->receive_frame` 也是最后调用这个函数进行解码的）

这里的 `avctx->codec` 是一个 `AVCodec` 类型的结构体，每个结构体代表了一种类型的解码器，h264 解码器的 `AVCodec` 结构体初始值如下（代码位于 `libavcodec\h264dec.c`）

```c
AVCodec ff_h264_decoder = {
    .name                  = "h264",
    .long_name             = NULL_IF_CONFIG_SMALL("H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10"),
    .type                  = AVMEDIA_TYPE_VIDEO,
    .id                    = AV_CODEC_ID_H264,
    .priv_data_size        = sizeof(H264Context),
    .init                  = h264_decode_init,
    .close                 = h264_decode_end,
    .decode                = h264_decode_frame,
    .capabilities          = /*AV_CODEC_CAP_DRAW_HORIZ_BAND |*/ AV_CODEC_CAP_DR1 |
                             AV_CODEC_CAP_DELAY | AV_CODEC_CAP_SLICE_THREADS |
                             AV_CODEC_CAP_FRAME_THREADS,
    .hw_configs            = (const AVCodecHWConfigInternal *const []) {
#if CONFIG_H264_DXVA2_HWACCEL
                               HWACCEL_DXVA2(h264),
#endif
#if CONFIG_H264_D3D11VA_HWACCEL
                               HWACCEL_D3D11VA(h264),
#endif
#if CONFIG_H264_D3D11VA2_HWACCEL
                               HWACCEL_D3D11VA2(h264),
#endif
#if CONFIG_H264_NVDEC_HWACCEL
                               HWACCEL_NVDEC(h264),
#endif
#if CONFIG_H264_VAAPI_HWACCEL
                               HWACCEL_VAAPI(h264),
#endif
#if CONFIG_H264_VDPAU_HWACCEL
                               HWACCEL_VDPAU(h264),
#endif
#if CONFIG_H264_VIDEOTOOLBOX_HWACCEL
                               HWACCEL_VIDEOTOOLBOX(h264),
#endif
                               NULL
                           },
    .caps_internal         = FF_CODEC_CAP_INIT_THREADSAFE | FF_CODEC_CAP_EXPORTS_CROPPING |
                             FF_CODEC_CAP_ALLOCATE_PROGRESS | FF_CODEC_CAP_INIT_CLEANUP,
    .flush                 = h264_decode_flush,
    .update_thread_context = ONLY_IF_THREADS_ENABLED(ff_h264_update_thread_context),
    .profiles              = NULL_IF_CONFIG_SMALL(ff_h264_profiles),
    .priv_class            = &h264_class,
};
```

其中 `decode` 成员对应的是 `h264_decode_frame` 函数，说明最后编码用的是这个函数