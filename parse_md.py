import re
import os
import glob
import random
import urllib.parse
import hashlib

mdFilePaths = glob.glob("docs/**/*.md", recursive=True)
# print(mdFilePaths)
# mdFiles = glob.glob("*.md")

latexInLinePattern = r"\$([^\$]+)\$"
latexBlockPattern = r"\$\$([^\$]+)\$\$"
picUrlPattern = r"!\[(.*)\]\(<?([^<^>]+?)>?\)"
notionExportNamePattern = r" [a-z0-9]{32}"
leftBracketPattern = r"（"
rightBracketPattern = r"）"

for mdFilePath in mdFilePaths:
    mdFile = os.path.basename(mdFilePath)
    mdFileDir = os.path.dirname(mdFilePath)
#     if mdFile == "SUMMARY.md":
#         continue

    
    newMdFile = re.sub(notionExportNamePattern, "", mdFile).replace(" ","_")

    # 保证文件名相同时生成图片的随机数名相同，尽量防止 git 重复删除加入图片
    seed = int(hashlib.md5(newMdFile.encode("utf-8")).hexdigest(), 16) % 1e7
    random.seed(seed)

    with open(mdFilePath, "r", encoding="utf-8") as f:
        print(f"Parse {mdFile} (seed {seed})")
        content = f.read()

#     # # replace latex formula
#     # content = re.sub(latexInLinePattern, r"\\\\( \g<1> \\\\)", content)
#     # content = re.sub(latexInLinePattern, r"\\\\(\\\\( \g<1> \\\\)\\\\)", content)

#     # # replace bracket
#     # content = re.sub(leftBracketPattern, r"  \(", content)
#     # content = re.sub(rightBracketPattern, r"\)  ", content)

    # process image
    # FIXME: 遇到 markdown 两次引用同一张图片时会有问题
    # 目的1：保证图片前缀为 md 文件名，后缀为随机数
    # 目的2：删除多余没有被任何 md 文件引用的图片
    if not os.path.isdir(os.path.join(mdFileDir, "markdown_images")):
        os.mkdir(os.path.join(mdFileDir, "markdown_images"))
    pics = re.findall(picUrlPattern, content)
    picRemoveList = []
    for (idx,pic) in enumerate(pics):
        (picName, picPath) = pic

        picPathDecode = urllib.parse.unquote(picPath)

        # 图片文件名符合要求，则此轮循环结束
        if os.path.basename(picPathDecode).startswith(newMdFile[:-3]):
            continue

        newPicPath = f"markdown_images/{newMdFile[:-3]}_{random.randint(0,10000)}.{picPathDecode.split('.')[-1]}"
        while os.path.isfile(os.path.join(mdFileDir, newPicPath)):
            newPicPath = f"markdown_images/{newMdFile[:-3]}_{random.randint(0,10000)}.{picPathDecode.split('.')[-1]}"
        newPicPathEncode = urllib.parse.quote(newPicPath)
        newPicName = os.path.basename(newPicPath).split(".")[0]

        # print(f"picPathDecode={picPathDecode}")
        # print(f"newPicPath={newPicPath}")
        # print(f"newPicName={newPicName}")

        with open(os.path.join(mdFileDir, picPathDecode), "rb") as f:
            picData = f.read()
        
        with open(os.path.join(mdFileDir, newPicPath), "wb") as f:
            f.write(picData)

        print(f"Move {picPathDecode} to {newPicPath}")

        content = re.sub(r"\(\<?"+picPath+r"\>?\)", f"({newPicPathEncode})", content)
        content = re.sub(r"\["+picName+r"\]", f"[{newPicName}]", content)
        
        picRemoveList.append(picPathDecode)
    for pic in set(picRemoveList):
        os.remove(os.path.join(mdFileDir, pic))

    # rename markdown file and clear the notion exported dir
    with open(os.path.join(mdFileDir, newMdFile), "w", encoding="utf-8") as f:
        f.write(content)
    if newMdFile != mdFile:
        print(f"Move {mdFile} to {newMdFile}")
        os.remove(mdFilePath)
        notionImagePath = os.path.join(mdFileDir, mdFile[:-3].split('_')[-1])
        if os.path.isdir(notionImagePath):
            print(f"Remove {notionImagePath} Directory")
            os.removedirs(notionImagePath)
        else:
            # for debug
            print(f"{notionImagePath} is not a dir")
        
    # update summary
    with open("_sidebar.md", "r", encoding="utf-8") as f:
        content = f.read()
    if os.path.join(mdFileDir, newMdFile).replace('\\','/') not in content:
        # print(os.path.join(mdFileDir, newMdFile))
        with open("_sidebar.md", "a", encoding="utf-8") as f:
            f.write("\n")
            f.write(f"* [{newMdFile[:-3].split('_')[-1]}](<./{os.path.join(mdFileDir, newMdFile)}>)".replace('\\','/'))
            print(f"add {newMdFile} to SUMMARY")

# 删除无引用的图片
imgFilePaths = glob.glob("docs/**/*.png", recursive=True)
for imgFilePath in imgFilePaths:
    imgFileNameEnecode = urllib.parse.quote(os.path.basename(imgFilePath))
    # print(imgFileNameEnecode)
    mdFilePaths = glob.glob("docs/**/*.md", recursive=True)
    for mdFilePath in mdFilePaths:
        with open(mdFilePath, "r", encoding="utf-8") as f:
            content = f.read()
        if imgFileNameEnecode in content:
            break
    else:
        print(f"remove redundant image {imgFilePath}")
        os.remove(imgFilePath)