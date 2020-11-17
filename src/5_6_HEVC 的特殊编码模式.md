# HEVC 的特殊编码模式

### HEVC 的特殊编码模式

![5_6_HEVC 的特殊编码模式_0](<markdown_images/5_6_HEVC 的特殊编码模式_0.png>)

1. I_PCM 模式**跳过了预测编码和变换编码的所有步骤**，**直接编码像素值**，I_PCM 模式由 CU 层次的 `pcm_flag` 控制，用于传输的图片接近噪声（没有任何规律）导致目前的编码手段无效的情况
2. lossless mode 用于无损传输，其**跳过了会产生误差的残差 DCT 变换和编码部分（也跳过了 in-loop filter）**，**直接编码残差值**，由 CU 层次的 cu_transquant_bypass_flag 控制，可以做到一部分图片 lossy 模式传输而另一部分图片以 lossless mode 传输（mixed lossless/lossy coding）
3. transform skip mode 用于改善远程桌面、幻灯片等主要由文字和图片组成的视频序列的显示效果，其**对空域残差直接进行量化而不进行 DCT 变换**（？），只能使用于 4x4 大小的 TB，由 TB 层次的 `transform_skip_flag` 控制