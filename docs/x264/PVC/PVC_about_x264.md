# PVC about x264

# 1. 感知编码概述

感知编码是利用人类视觉系统的感知特性，通过消除感知冗余，提高主观质量，得到更高效率的编码。可达到以下两个目的或其中之一：

- 在保持主观质量不变的条件下，减少码率。
- 在码率保持不变的条件下，提高视频质量。

# 2. 考虑感知特性的相关参数

在x264中,预设值`tune`影响了编解码后输出视频的画质质量，它根据不同模式下的画质需求，设置了一系列参数，部分参数的设置考虑了人的心理视觉。

其中`tune`有以下8种类型。

- film：电影类型，对视频的质量要求严格时使用该选项
- animation：动画片，压缩的视频是动画片时使用该选项
- grain：颗粒物很重，该选项适用于颗粒物很重的视频
- stillimage：静态图像，该选项适用于静止画面比较多的视频
- psnr：提高psnr，该选项编码出来的psnr比较高
- ssim：提高ssim，改选项编码出来的ssim比较高
- fastdecode：快速解码，该选项有利于快速解码
- zerolatency：零延迟编码，该选项主要用于视频直播

考虑心理视觉的模式有film,animation,grain, stillimage,psnr,ssim,共计6种，称作为psy_tune,psy是单词psychovisual的简称。值得注意的是，设置命令行参数时，可以使用多个tune，但psy_tune仅能使用一个。

不同`tune`下的具体参数在此不再赘述。其中和心理视觉相关的参数主要有

- `psy_rd`：影响率失真方程中码率和失真的平衡；默认值为1.0
- `psy_trellis`：网格量化强度；默认值为0.0
- `aq_strength`：自适应量化强度；默认值为1.0
- `aq_mode`：自适应量化模式；默认值为1.0
- `qcom` :码率缩放因子强度，默认值为0.6

不难看出，上述参数主要应用在率失真优化以及量化、码率控制中，可以分开讨论。

# 3. 率失真优化

## 3.1 率失真优化概述

RDO全称为Rate-Distortion Optimization，中文为率失真优化，在视频编码过程中，它是平衡编码失真和码率的优化手段。我们可以将率失真优化表述为在目标码率受限制条件下，使得编码失真达到最小。

一般用R表示码率函数，用D表示编码失真函数，根据凸优化理论，当R和D都为凸函数时，目标函数可表示为拉格朗日函数的形式：

$min{J=R+\lambda*D}$

此时求解该函数，可得到

$\lambda=-\frac{\partial{R}}{\partial{D}}$

于是我们可知，lambada值的大小影响着编码失真和码率的平衡程度，其值越小，压缩程度越高，码率越低，失真程度越高，其值越大，压缩程度越低，码率越高，失真程度越低。所以，lamda值的大小直接决定着最优编码参数的选择，需对lambda值进行量化分析，通过实验得到计算公式。

率失真方程在码率控制，模式选择和运动估计中都有应用。

值得注意的是，在x264中，以帧内预测过程为例，进行模式决策时，所调用的`mb_analyse_intra` 和在`mbrd`可用时调用的`intra_rd` 两者计算率失真方程的方式不一样。

```c
mb_analyse_intra( h, &analysis, COST_MAX );
        if( analysis.i_mbrd )
            intra_rd( h, &analysis, COST_MAX );
```

不同之处有两点。

- 第一，码率计算方式不同。前者计算时为减少计算量，没有对每一种模式进行编码，而是采用查表的方法计算码率R，查找表为`x264_ue_size_tab` （查找表对应的应该有mode、mv和残差的比特数，所以可以理解为什么每一个QP都对应一个最优的lambda）；而后者需要重建宏块，获得熵编码信息，从而计算实际码率R。在帧间预测等其他地方也是做类似处理。
- 第二，率失真方程表达式不同。仍以帧内预测为例，当分析亮度像素且`psy_rd` 非0时，前者率失真方程为$cost=satd+lambda*R$；后者为$cost=ssd+psy\_    rd*lambda*satd+lambda2*R$，用更大的lambda2系数大概是因为失真D变大了。准确的公式附带移位操作。

后文所说的RDO皆是后者，因为从实际应用和分析可知，`psy_rd` 应用在前者并不能达到码率和失真的更好平衡，反而可能会破坏码率控制的效果。

## 3.2 `psy_rd` 应用

官方提供的对`psy_rd`的描述是

we would rather see a somewhat distorted but still detailed block than a non-distorted but completely blurred block. The result is a bias towards a detailed and/or grainy output image, a bit like xvid except that its actual detail rather than ugly blocking。

意指`psy_rd` 能够把比特位分配到背景，减小图像的模糊现象，增添更多的细节。

在x264源码中，`psy_rd` 应用在三个地方。

第一，`psy_rd` 主要用于宏块级SATD的计算。当`psy_rd` 有效时，会成为SATD的调控因子，代码位于rdo.c的第144行，属于ssd_plain()函数。

```c
satd = (satd * h->mb.i_psy_rd * h->mb.i_psy_rd_lambda + 128) >> 8;
```

可以发现，`pst_rd` 相当于一个惩罚项，相比普通的RD，无论编码宏块是平滑的还是高复杂度的，它对偏离参考宏块更多satd的决策有更大的惩罚。如果从结果推过程的话，它对使宏块平坦的决策惩罚更大，从而在码率充足的条件下能够得到细节更多，颗粒度更多的画面，反之同理。具体的原因需要后续研究一下SATD的性质了。

其中ssd_plain()的调用关系如下。

![PVC_about_x264_4572751872](markdown_images/PVC_about_x264_4572751872.png)

可见，经过`psy_rd` 调控的率失真方程被用于宏块分析中的帧内预测、块划分、帧间预测及其MV估计、QP调整等需权衡码率和失真的地方。

第二，`psy_rd` 增大，会使模式判决提前终止的概率减小。

```c
if( a->b_early_terminate && (!i && i_part_cost + a->i_cost_est16x8[1] > i_best_satd
            * (16 + (!!a->i_mbrd + !!h->mb.i_psy_rd))/16) )
```

第三，为得到质量更好的重建宏块，在`macroblock_analyse()` 宏块分析函数结束处（帧内帧间预测结束，变换量化之前），由`mbrd` 决定是否调用`mb_analyse_qp_rd()` 提前编码一次，计算率失真方程，可以调整QP值的大小。具体的例子是

假如，QP初始值是25，模式决策后，得到satd值为20，此时调用`mb_analyse_qp_rd()` 重新编码，发现cbp的6bit全为0，这意味着亮度和色度信号的DCT系数都为0，于是调小QP值，减少细节损失。

具体的调控方式见代码analyse.c的第2841行，简单来说，`psy_rd` 初始化阈值`threshold`，`psy_rd` 越大，阈值越大，函数提前跳出的概率会越小，当QP调控方向`direction` 为-1也就是QP倾向变小时，分配的QP值会更小。见下述代码。

```c
h->mb.i_qp = X264_MAX( h->mb.i_qp - threshold - 1, SPEC_QP( h->param.rc.i_qp_min ) );
                h->mb.i_chroma_qp = h->chroma_qp_table[h->mb.i_qp];
```

## 3.3 `psy_rd` 控制关系

上述提到的应用并不总是有效，在宏块分析时，会根据`mbrd`的大小控制率失真优化的程度。换言之，`mbrd` 影响包括`psy_rd` 参数在内的整个率失真优化过程。`mbrd` 在analysis_init（)初始化定义如下。

```c
		/* mbrd == 1 -> RD mode decision */
    /* mbrd == 2 -> RD refinement */
    /* mbrd == 3 -> QPRD */
    a->i_mbrd = (subme>=6) + (subme>=8) + (h->param.analyse.i_subpel_refine>=10);
```

`mbrd` 由`subme` 和`subpel_refine` 两个参数确定大小，只用当`subme≥6`时才会启用RDO，`psy_rd`才能有效。

`subme`参数说明如下。

设定子像素（subpixel）估算复杂度。值越高越好。层级1~5只是控制子像素细分（refinement）强度。层级6为**模式决策**启用RDO，而层级8为**动态向量**和**内部预测模式**启用RDO。RDO层级明显慢于先前的层级。

可用的值：

`0`：Fullpel only`1`：QPel SAD 1 iteration`2`：QPel SATD 2 iterations`3`：HPel on MB then QPel`4`：Always QPel`5`：Multi QPel + bi-directional motion estimation`6`：RD on I/P frames`7`：RD on all frames`8`：RD refinement on I/P frames`9`：RD refinement on all frames`10`：QP-RD (requires `--[trellis](https://www.nmm-hd.org/doc/X264%E8%A8%AD%E5%AE%9A#trellis)`=2, `--[aq-mode](https://www.nmm-hd.org/doc/X264%E8%A8%AD%E5%AE%9A#aq-mode)`>0)`11`：Full RD: disable all early terminations。

可参考的测试结论（[https://www.cnblogs.com/cmt/p/14553189.html](https://www.cnblogs.com/cmt/p/14553189.html)）

- subme10比起subme9，更偏向于节省码率，因此造成了画质的轻微下降，同时转码速度有所下降。subme11再次大幅降低了转码速度，但在画质、码率方面与subme10几乎一致，不推荐。如果追求压缩率，推荐使用subme10；如果追求画质，推荐使用subme9。

# 4. 网格量化

## 4.1 网格量化概述

我们一般所知的量化方法为标量量化，它是为给定系数选择最接近的量化值，在给定QP下可以使量化误差最小，但对码率缺少考虑。网格量化英文全称是trellis quantization，可以理解为用动态规划的方法，权衡码率和失真，搜寻最佳路径，从而选择最佳的量化方式。

## 4.2 x264中的网格量化

在x264中，量化部分代码的调用关系如下。

![PVC_about_x264_3548060672](markdown_images/PVC_about_x264_3548060672.png)

宏块编码能够依据色度和亮度的不同，不同的宏块类型进行变换、量化，从而重构宏块。其中编码过程存在两种量化方式。

第一种是H.264标准文档提到的量化方式，在量化的同时完成了DCT变换中系数相乘的工作。

```c
/*量化公式：
|Zij| = (|Wij|*MF + f)>>qbits 
sign(Zij) = sign (Wij)
*/
#define QUANT_ONE( coef, mf, f ) \
{ \
    if( (coef) > 0 ) \
        (coef) = (f + (coef)) * (mf) >> 16; \
    else \
        (coef) = - ((f - (coef)) * (mf) >> 16); \
    nz |= (coef); \
}
```

第二种是我们现在提及的网格量化，是伴随率失真决策来选择量化值的。为方便分析，以C语言版本的`quant_trellis_cacbc()` 中的`TRELLIS_LOOP(0)`网格量化流程为例，仅是简要概括。

**step1** 初始化各结构体

`trellis_level_t level_tree[64*8*2]` :存储所有系数在不同水平的最佳量化路径。

64——最大系数容量      8——CACBC中上下文状态的8种情况，由大于1和等于1的系数数量决定                          2——两个量化水平

`trellis_node_t  *nodes_pre`  :前一个节点，结构体信息包含score、level_idx、cacbc_state[4]（状态转移情况最多四种）

`trellis_node_t  *nodes_cur`  :当前节点。

**step2** 开始反向遍历所有系数

- 进行基础量化
    - 遍历两个量化水平{q,q-1}
    - 计算带权重的量化系数差值`ssd0`和`ssd1`
        - 根据系数的可能值计算`score` ，`score`是率失真方程，失真D是ssd，码率R是CACBC的累计码率，确定各上下文状态的最低`score` ，返回`level_used` 。

            ```c
            switch( q )\
                    {\
                    case 1:\
                        ssd1[0] += (uint64_t)cost_siglast[0] * lambda2 >> ( CABAC_SIZE_BITS - LAMBDA_BITS );\
                        levels_used = trellis_coef0_##ctx_hi( ssd0[0]-ssd1[0], nodes_cur, nodes_prev, level_tree, levels_used );\
                        levels_used = trellis_coef1_##ctx_hi( ssd0[1]-ssd1[0], ssd1[1]-ssd1[0], cost_siglast, nodes_cur, nodes_prev, level_tree, levels_used, lambda2, level_state );\
                        goto next##ctx_hi;\
                    case 2:\
                        levels_used = trellis_coef1_##ctx_hi( ssd0[0], ssd1[0], cost_siglast, nodes_cur, nodes_prev, level_tree, levels_used, lambda2, level_state );\
                        levels_used = trellis_coefn_##ctx_hi( q, ssd0[1], ssd1[1], cost_siglast, nodes_cur, nodes_prev, level_tree, levels_used, lambda2, level_state, levelgt1_ctx );\
                        goto next1;\
                    default:\
                        levels_used = trellis_coefn_##ctx_hi( q-1, ssd0[0], ssd1[0], cost_siglast, nodes_cur, nodes_prev, level_tree, levels_used, lambda2, level_state, levelgt1_ctx );\
                        levels_used = trellis_coefn_##ctx_hi( q, ssd0[1], ssd1[1], cost_siglast, nodes_cur, nodes_prev, level_tree, levels_used, lambda2, level_state, levelgt1_ctx );\
                        goto next1;\
                    }\
            ```

            `trellis_coef0_0()` ：传递`*nodes_pre` 的结构体信息给`*nodes_cur` ，更新`level_tree` 新节点信息,方便回溯。

            `trellis_coef0_1()` ：解决最短路径问题，权重是`score` ，码率是累加的，代表截止目前各ctx搜寻的最佳量化路径。对于`TRELLIS_LOOP(0)` ，只有4种ctx的上下文状态，而且每次都从ctx0开始遍历，所以分别计算在当前系数当前量化水平下的 4种ctx的最佳量化路径，也就是4个最小的`score`。状态转移部分没有细看。

        - 更新上下文状态信息
- 更新四个节点路径信息

**step3**  输出level_tree的最佳路径和量化水平

## 4.3 `psy_trellis` 应用

在4.2提到的网格量化过程中，如果`psy_trellis` 被启用，可以作为权重调控ssd1的实际大小，代码位于rdo.c的`quant_trellis_cabac()` 函数。

```c
/* Psy trellis: bias in favor of higher AC coefficients in the reconstructed frame. */\
if( h->mb.i_psy_trellis && i && !dc && !b_chroma )\
    {\
      int orig_coef = (num_coefs == 64) ? h->mb.pic.fenc_dct8[idx][zigzag[i]] : h->mb.pic.fenc_dct4[idx][zigzag[i]];\
      int predicted_coef = orig_coef - sign_coef;\
      int psy_value = abs(unquant_abs_level + SIGN(predicted_coef, sign_coef));\
      int psy_weight = coef_weight1[zigzag[i]] * h->mb.i_psy_trellis;/*coef_weight是归一化权重*/\
      ssd1[k] = (uint64_t)d*d * coef_weight2[zigzag[i]] - psy_weight * psy_value;/*计算两种量化方式的ssd*/\
    }\
```

正如注释中提到的，`psy_trellis`能够反映重建帧中使用AC系数的高低偏好。`psy_trellis` 值减小，ssd增小，对失真的容忍度变低，AC系数量化损失变小。

另外，`psy_trellis` 和`psy_rd` 在提高亮度色块的质量时，间接损害了色度块的质量，所以会对色度块的QP值进行补偿。

```c
/* Psy RDO increases overall quantizers to improve the quality of luma--this indirectly hurts chroma quality */
    /* so we lower the chroma QP offset to compensate */
    if( b_open && h->mb.i_psy_rd && !h->param.i_avcintra_class )
        h->param.analyse.i_chroma_qp_offset -= h->param.analyse.f_psy_rd < 0.25 ? 1 : 2;
    /* Psy trellis has a similar effect. */
    if( b_open && h->mb.i_psy_trellis && !h->param.i_avcintra_class )
        h->param.analyse.i_chroma_qp_offset -= h->param.analyse.f_psy_trellis < 0.25 ? 1 : 2;
    h->param.analyse.i_chroma_qp_offset = x264_clip3(h->param.analyse.i_chroma_qp_offset, -12, 12);
```

# 5. 码率控制

## 5.1 码率控制概述

- 概念：采取一定的算法对编码器输出的码流进行控制，使得输出码流能够适应各种信道。
- 控制模型：帧级目标比特分配、片级目标比特分配、RDO控制模型和码率控制状态更新模块。
- x264有五种帧级的码率控制方法:CQP（恒定QP）、CRF（默认，视觉质量稳定）、ABR（码率平均）、2-pass（2次编码）、CBV（恒定码率，由VBV大小决定码率分配）。

    前三种是显式定义的方法，后两种需要额外信息调控实现。概念区别可见[Waht are CBR,VBV and CPB?](https://codesequoia.wordpress.com/2010/04/19/what-are-cbr-vbv-and-cpb/)，x264帧级的码率控制实现区别可见[不同方法的实现区别](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/c0ace854-4ef2-4a1d-9698-4190f4d8515a/ratecontrol.txt?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAT73L2G45O3KS52Y5%2F20210325%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20210325T040736Z&X-Amz-Expires=86400&X-Amz-Signature=26444b59247fcd04a17d69f4575cd7ca541d05ba2cd7494c23b3c9538b5a761e&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22ratecontrol.txt%22)。

## 5.2 `aq_strength` 和`aq_mode`参数应用

`aq_strength` 和`aq_mode` 同时出现在自适应量化控制函数`x264_adaptive_quant_frame()` ，该函数运行在帧类型判定和参考帧管理之后，帧级编码之前，用于计算各宏块的QP偏移值，仅在`mb_tree` 禁用且编码为multipass时才不被调用。

当`aq_strength` 和`aq_mode` 都非0有效时，函数进行自适应量化，依据宏块复杂度控制各宏块的QP偏移值。各模式的控制强度如下。

- `aq_mode=2 or 3` ：$strength=h->param.rc.f\_aq\_strength*avg\_adj$
- `aq_mode=1` :$strength=h->param.rc.f\_aq\_strength*1.0397f$

各模式偏移值如下

- `aq_mode=1` ：$qp\_adj = strength * (x264\_log2( X264\_MAX(energy, 1) ) - (14.427f + 2*(BIT\_DEPTH-8)))$
- `aq_mode=2` ：$qp\_adj = strength * (qp\_adj - avg\_adj)$
- `aq_mode=3` ：$qp\_adj = strength * (qp\_adj - avg\_adj) + bias\_strength * (1.f - 14.f / (qp\_adj * qp\_adj))$

从公式可以看出，`aq_strength`是QP偏移值的系数；`aq_mode` 从函数关系上影响着QP偏移值的幅度,有对数、正比、线性相加三种关系，动态范围依次增大。

另外，方程用像素域局部方差和全局方差的差值影响QP偏移值，这将使纹理显著性区域比平坦区域在QP的调节上拥有更大的动态范围，这么做是基于人眼的掩蔽效应，即人眼对平坦区域的失真比高细节区域的失真更敏感。

最终，QP偏移值在`x264_ratecontrol_mb_qp()`函数应用，在该函数中，对每个宏块在原先的QP基础上再加上`x264_adaptive_quant_frame()`计算出来的QP偏移值。

测试实验显示，默认的`aq_strength` =1和`aq_mode` =1效果会比`aq_strength` =2和`aq_mode` =2好一些。可以简单对比测试视频的第十七帧。

![PVC_about_x264_2039064576](markdown_images/PVC_about_x264_2039064576.png)

（a）QP=24.65,aq-mode=1，aq-strength=1

![PVC_about_x264_3818587136](markdown_images/PVC_about_x264_3818587136.png)

（b）QP=24.50,aq-mode=2，aq-strength=2

## 5.3 `qcom` 参数应用

`qcom` 在编码器解析参数时，被替换为`f_compress` ，注释上注明是调节压缩视频的QP曲线，`qcompress` 趋于0，码率控制方法趋向CBR，`qcompress` 趋于1，码率控制方法趋向CQP。

```c
H2( "--qcomp <float>         QP curve compression [%.2f]\n", defaults->rc.f_qcompress );
```

`qcompress` 主要应用在CRF(恒定质量)，通过人为设置影响码率缩放因子，调整帧级的QP分配，可以得到稳定的视频质量。具体过程如下。

- 在开启编码器执行`encode_open()` 时，调用`x264_ratecontrol_new` 中的`x264_ratecontrol_init_reconfigurable` ，此时`qcompress` 调整码率缩放因子rate_factor_constant。

    ```c
    if( h->param.rc.i_rc_method == X264_RC_CRF )
        {
            /* Arbitrary rescaling to make CRF somewhat similar to QP.
             * Try to compensate for MB-tree's effects as well. */
            double base_cplx = h->mb.i_mb_count * (h->param.i_bframe ? 120 : 80);
            double mbtree_offset = h->param.rc.b_mb_tree ? (1.0-h->param.rc.f_qcompress)*13.5 : 0;
            rc->rate_factor_constant = pow( base_cplx, 1 - rc->qcompress )
                                     / qp2qscale( h->param.rc.f_rf_constant + mbtree_offset + QP_BD_OFFSET );
        }
    ```

- 开始逐帧编码时，由函数`rate_estimate_qscale()` 根据SATD值、目标码率和目前实际码率计算出当前帧量化参数尺度值(qscale)，然后由码率缩放因子rate_factor_consatnt调整qpscale的值，使得编码速率尽可能接近所要求的平均比特率，再通过`qscale2qp()`函数计算出当前帧量化参数QP。

值得注意的是，上述的控制方程在宏块级的[mb_tree](https://blog.csdn.net/zhoudegui88/article/details/80221765)关闭和开启时效果调控不一样，现今[mb_tree](https://blog.csdn.net/zhoudegui88/article/details/80221765) 是默认开启的，因为它是除自适应量化外的另一种宏块级量化调整方法，可以得到更好的视觉质量。