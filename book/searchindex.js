Object.assign(window.search, {"doc_urls":["HEVC 的基本介绍.html#hevc-的基本介绍","HEVC 的基本流程.html#hevc-的基本流程"],"index":{"documentStore":{"docInfo":{"0":{"body":45,"breadcrumbs":1,"title":1},"1":{"body":12,"breadcrumbs":1,"title":1}},"docs":{"0":{"body":"HEVC 全称 High Efficiency Video Coding，是 用于替代 ITU-T H.264/MPEG-4 AVC 的下一代编码标准 ，于 2013 年 正式启用（成为国际标准），其由 来自 ISO/IEC 的 MPEG （Moving Picture Experts Group） 小组和来自 ITU-T 的 VCEG （Video Coding Experts Group） 小组共同组成的 JCT-VC （Joint Collaborative Team on Video Coding） 小组 制定，在 ISO/IEC 中作为 MPEG-H Part 2 (ISO/IEC 23008-2) 标准，在 ITU-T 中作为 H.265 标准，其特点为 相比 H.264 标准在相同画面质量下节省码率 50% 可从 此网站 下载 HEVC 官方文档","breadcrumbs":"HEVC 的基本介绍","id":"0","title":"HEVC 的基本介绍"},"1":{"body":"image-20201109003052560 HEVC 使用 基于块的混合编码技术 ，混合是指其同时使用了 预测编码 和 变换编码 的技术，预测编码指其 利用时域和空域的邻近像素预测当前像素值，之后传输实际值与预测值之差 ，变换编码指其 对残差执行了 DCT 变换，传输其量化后的非零 DCT 系数 HEVC 的具体流程为首先对图片进行 分块操作 ，然后以块为单位对图片进行 帧内编码 或 帧间编码 ，然后进行 帧内编码预测 或 帧间编码预测 得到图片的 第一次重建图像 （称为 预测图像 ），拿图片原图减去第一次重建图像得到 残差 ，将残差进行 DCT变换 、 量化 再进行 反 DCT 变换 得到 重建残差 ，将第一次重建图像加上重建残差得到 第二次重建图像 ，第二次重建图像进行 环路滤波 （in-loop filter）得到得到 第三次重建图像 （称为 重建图像 ），第三次重建图像是最终解码的结果，将其 存入 buffer 用作编码顺序之后帧帧间编码的参考，编码中产生的帧内/帧间编码的数据和残差（以及其它控制信号）则经过 熵编码 之后作为编码输出，之后帧的编码过程与此相同 由图可知， HEVC 的编码器中嵌套了一个完整的解码器","breadcrumbs":"HEVC 的基本流程","id":"1","title":"HEVC 的基本流程"}},"length":2,"save":true},"fields":["title","body","breadcrumbs"],"index":{"body":{"root":{"2":{"0":{"1":{"3":{"df":1,"docs":{"0":{"tf":1.0}}},"df":0,"docs":{}},"2":{"0":{"1":{"1":{"0":{"9":{"0":{"0":{"3":{"0":{"5":{"2":{"5":{"6":{"0":{"df":1,"docs":{"1":{"tf":1.0}}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"3":{"0":{"0":{"8":{"df":1,"docs":{"0":{"tf":1.0}}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":1,"docs":{"0":{"tf":1.4142135623730951}}},"4":{"df":1,"docs":{"0":{"tf":1.0}}},"5":{"0":{"df":1,"docs":{"0":{"tf":1.0}}},"df":0,"docs":{}},"a":{"df":0,"docs":{},"v":{"c":{"df":1,"docs":{"0":{"tf":1.0}}},"df":0,"docs":{}}},"b":{"df":0,"docs":{},"u":{"df":0,"docs":{},"f":{"df":0,"docs":{},"f":{"df":0,"docs":{},"e":{"df":0,"docs":{},"r":{"df":1,"docs":{"1":{"tf":1.0}}}}}}}},"c":{"df":0,"docs":{},"o":{"d":{"df":0,"docs":{},"e":{"df":1,"docs":{"0":{"tf":1.7320508075688772}}}},"df":0,"docs":{},"l":{"df":0,"docs":{},"l":{"a":{"b":{"df":0,"docs":{},"o":{"df":0,"docs":{},"r":{"df":1,"docs":{"0":{"tf":1.0}}}}},"df":0,"docs":{}},"df":0,"docs":{}}}}},"d":{"c":{"df":0,"docs":{},"t":{"df":1,"docs":{"1":{"tf":2.0}}}},"df":0,"docs":{}},"df":0,"docs":{},"e":{"df":0,"docs":{},"f":{"df":0,"docs":{},"f":{"df":0,"docs":{},"i":{"c":{"df":0,"docs":{},"i":{"df":1,"docs":{"0":{"tf":1.0}}}},"df":0,"docs":{}}}},"x":{"df":0,"docs":{},"p":{"df":0,"docs":{},"e":{"df":0,"docs":{},"r":{"df":0,"docs":{},"t":{"df":1,"docs":{"0":{"tf":1.4142135623730951}}}}}}}},"f":{"df":0,"docs":{},"i":{"df":0,"docs":{},"l":{"df":0,"docs":{},"t":{"df":0,"docs":{},"e":{"df":0,"docs":{},"r":{"df":1,"docs":{"1":{"tf":1.0}}}}}}}},"g":{"df":0,"docs":{},"r":{"df":0,"docs":{},"o":{"df":0,"docs":{},"u":{"df":0,"docs":{},"p":{"df":1,"docs":{"0":{"tf":1.4142135623730951}}}}}}},"h":{".":{"2":{"6":{"4":{"/":{"df":0,"docs":{},"m":{"df":0,"docs":{},"p":{"df":0,"docs":{},"e":{"df":0,"docs":{},"g":{"df":1,"docs":{"0":{"tf":1.0}}}}}}},"df":1,"docs":{"0":{"tf":1.0}}},"5":{"df":1,"docs":{"0":{"tf":1.0}}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":1,"docs":{"0":{"tf":1.0}},"e":{"df":0,"docs":{},"v":{"c":{"df":2,"docs":{"0":{"tf":1.7320508075688772},"1":{"tf":2.0}}},"df":0,"docs":{}}},"i":{"df":0,"docs":{},"g":{"df":0,"docs":{},"h":{"df":1,"docs":{"0":{"tf":1.0}}}}}},"i":{"df":0,"docs":{},"m":{"a":{"df":0,"docs":{},"g":{"df":1,"docs":{"1":{"tf":1.0}}}},"df":0,"docs":{}},"s":{"df":0,"docs":{},"o":{"/":{"df":0,"docs":{},"i":{"df":0,"docs":{},"e":{"c":{"df":1,"docs":{"0":{"tf":1.7320508075688772}}},"df":0,"docs":{}}}},"df":0,"docs":{}}},"t":{"df":0,"docs":{},"u":{"df":1,"docs":{"0":{"tf":1.7320508075688772}}}}},"j":{"c":{"df":0,"docs":{},"t":{"df":1,"docs":{"0":{"tf":1.0}}}},"df":0,"docs":{},"o":{"df":0,"docs":{},"i":{"df":0,"docs":{},"n":{"df":0,"docs":{},"t":{"df":1,"docs":{"0":{"tf":1.0}}}}}}},"l":{"df":0,"docs":{},"o":{"df":0,"docs":{},"o":{"df":0,"docs":{},"p":{"df":1,"docs":{"1":{"tf":1.0}}}}}},"m":{"df":0,"docs":{},"o":{"df":0,"docs":{},"v":{"df":0,"docs":{},"e":{"df":1,"docs":{"0":{"tf":1.0}}}}},"p":{"df":0,"docs":{},"e":{"df":0,"docs":{},"g":{"df":1,"docs":{"0":{"tf":1.4142135623730951}}}}}},"p":{"a":{"df":0,"docs":{},"r":{"df":0,"docs":{},"t":{"df":1,"docs":{"0":{"tf":1.0}}}}},"df":0,"docs":{},"i":{"c":{"df":0,"docs":{},"t":{"df":0,"docs":{},"u":{"df":0,"docs":{},"r":{"df":1,"docs":{"0":{"tf":1.0}}}}}},"df":0,"docs":{}}},"t":{"df":1,"docs":{"0":{"tf":1.7320508075688772}},"e":{"a":{"df":0,"docs":{},"m":{"df":1,"docs":{"0":{"tf":1.0}}}},"df":0,"docs":{}}},"v":{"c":{"df":1,"docs":{"0":{"tf":1.0}},"e":{"df":0,"docs":{},"g":{"df":1,"docs":{"0":{"tf":1.0}}}}},"df":0,"docs":{},"i":{"d":{"df":0,"docs":{},"e":{"df":0,"docs":{},"o":{"df":1,"docs":{"0":{"tf":1.7320508075688772}}}}},"df":0,"docs":{}}}}},"breadcrumbs":{"root":{"2":{"0":{"1":{"3":{"df":1,"docs":{"0":{"tf":1.0}}},"df":0,"docs":{}},"2":{"0":{"1":{"1":{"0":{"9":{"0":{"0":{"3":{"0":{"5":{"2":{"5":{"6":{"0":{"df":1,"docs":{"1":{"tf":1.0}}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"3":{"0":{"0":{"8":{"df":1,"docs":{"0":{"tf":1.0}}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":1,"docs":{"0":{"tf":1.4142135623730951}}},"4":{"df":1,"docs":{"0":{"tf":1.0}}},"5":{"0":{"df":1,"docs":{"0":{"tf":1.0}}},"df":0,"docs":{}},"a":{"df":0,"docs":{},"v":{"c":{"df":1,"docs":{"0":{"tf":1.0}}},"df":0,"docs":{}}},"b":{"df":0,"docs":{},"u":{"df":0,"docs":{},"f":{"df":0,"docs":{},"f":{"df":0,"docs":{},"e":{"df":0,"docs":{},"r":{"df":1,"docs":{"1":{"tf":1.0}}}}}}}},"c":{"df":0,"docs":{},"o":{"d":{"df":0,"docs":{},"e":{"df":1,"docs":{"0":{"tf":1.7320508075688772}}}},"df":0,"docs":{},"l":{"df":0,"docs":{},"l":{"a":{"b":{"df":0,"docs":{},"o":{"df":0,"docs":{},"r":{"df":1,"docs":{"0":{"tf":1.0}}}}},"df":0,"docs":{}},"df":0,"docs":{}}}}},"d":{"c":{"df":0,"docs":{},"t":{"df":1,"docs":{"1":{"tf":2.0}}}},"df":0,"docs":{}},"df":0,"docs":{},"e":{"df":0,"docs":{},"f":{"df":0,"docs":{},"f":{"df":0,"docs":{},"i":{"c":{"df":0,"docs":{},"i":{"df":1,"docs":{"0":{"tf":1.0}}}},"df":0,"docs":{}}}},"x":{"df":0,"docs":{},"p":{"df":0,"docs":{},"e":{"df":0,"docs":{},"r":{"df":0,"docs":{},"t":{"df":1,"docs":{"0":{"tf":1.4142135623730951}}}}}}}},"f":{"df":0,"docs":{},"i":{"df":0,"docs":{},"l":{"df":0,"docs":{},"t":{"df":0,"docs":{},"e":{"df":0,"docs":{},"r":{"df":1,"docs":{"1":{"tf":1.0}}}}}}}},"g":{"df":0,"docs":{},"r":{"df":0,"docs":{},"o":{"df":0,"docs":{},"u":{"df":0,"docs":{},"p":{"df":1,"docs":{"0":{"tf":1.4142135623730951}}}}}}},"h":{".":{"2":{"6":{"4":{"/":{"df":0,"docs":{},"m":{"df":0,"docs":{},"p":{"df":0,"docs":{},"e":{"df":0,"docs":{},"g":{"df":1,"docs":{"0":{"tf":1.0}}}}}}},"df":1,"docs":{"0":{"tf":1.0}}},"5":{"df":1,"docs":{"0":{"tf":1.0}}},"df":0,"docs":{}},"df":0,"docs":{}},"df":0,"docs":{}},"df":1,"docs":{"0":{"tf":1.0}},"e":{"df":0,"docs":{},"v":{"c":{"df":2,"docs":{"0":{"tf":2.0},"1":{"tf":2.23606797749979}}},"df":0,"docs":{}}},"i":{"df":0,"docs":{},"g":{"df":0,"docs":{},"h":{"df":1,"docs":{"0":{"tf":1.0}}}}}},"i":{"df":0,"docs":{},"m":{"a":{"df":0,"docs":{},"g":{"df":1,"docs":{"1":{"tf":1.0}}}},"df":0,"docs":{}},"s":{"df":0,"docs":{},"o":{"/":{"df":0,"docs":{},"i":{"df":0,"docs":{},"e":{"c":{"df":1,"docs":{"0":{"tf":1.7320508075688772}}},"df":0,"docs":{}}}},"df":0,"docs":{}}},"t":{"df":0,"docs":{},"u":{"df":1,"docs":{"0":{"tf":1.7320508075688772}}}}},"j":{"c":{"df":0,"docs":{},"t":{"df":1,"docs":{"0":{"tf":1.0}}}},"df":0,"docs":{},"o":{"df":0,"docs":{},"i":{"df":0,"docs":{},"n":{"df":0,"docs":{},"t":{"df":1,"docs":{"0":{"tf":1.0}}}}}}},"l":{"df":0,"docs":{},"o":{"df":0,"docs":{},"o":{"df":0,"docs":{},"p":{"df":1,"docs":{"1":{"tf":1.0}}}}}},"m":{"df":0,"docs":{},"o":{"df":0,"docs":{},"v":{"df":0,"docs":{},"e":{"df":1,"docs":{"0":{"tf":1.0}}}}},"p":{"df":0,"docs":{},"e":{"df":0,"docs":{},"g":{"df":1,"docs":{"0":{"tf":1.4142135623730951}}}}}},"p":{"a":{"df":0,"docs":{},"r":{"df":0,"docs":{},"t":{"df":1,"docs":{"0":{"tf":1.0}}}}},"df":0,"docs":{},"i":{"c":{"df":0,"docs":{},"t":{"df":0,"docs":{},"u":{"df":0,"docs":{},"r":{"df":1,"docs":{"0":{"tf":1.0}}}}}},"df":0,"docs":{}}},"t":{"df":1,"docs":{"0":{"tf":1.7320508075688772}},"e":{"a":{"df":0,"docs":{},"m":{"df":1,"docs":{"0":{"tf":1.0}}}},"df":0,"docs":{}}},"v":{"c":{"df":1,"docs":{"0":{"tf":1.0}},"e":{"df":0,"docs":{},"g":{"df":1,"docs":{"0":{"tf":1.0}}}}},"df":0,"docs":{},"i":{"d":{"df":0,"docs":{},"e":{"df":0,"docs":{},"o":{"df":1,"docs":{"0":{"tf":1.7320508075688772}}}}},"df":0,"docs":{}}}}},"title":{"root":{"df":0,"docs":{},"h":{"df":0,"docs":{},"e":{"df":0,"docs":{},"v":{"c":{"df":2,"docs":{"0":{"tf":1.0},"1":{"tf":1.0}}},"df":0,"docs":{}}}}}}},"lang":"English","pipeline":["trimmer","stopWordFilter","stemmer"],"ref":"id","version":"0.9.5"},"results_options":{"limit_results":30,"teaser_word_count":30},"search_options":{"bool":"OR","expand":true,"fields":{"body":{"boost":1},"breadcrumbs":{"boost":1},"title":{"boost":2}}}});