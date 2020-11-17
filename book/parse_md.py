import re
import os
import glob
import urllib.parse

# f = open("markdown_images/Untitled-1604937040052.png")

# print(os.path.isdir("QP 推断 e8bb4ab08c91470e89db29b5e43fa3c2"))

mdFiles = glob.glob("*.md")

latexInLinePattern = r"\$([^\$]+)\$"
latexBlockPattern = r"\$\$([^\$]+)\$\$"
picUrlPattern = r"!\[(.*)\]\(<?([^<^>]+?)>?\)"
notionExportNamePattern = r" [a-z0-9]{32}"
leftBracketPattern = r"（"
rightBracketPattern = r"）"

for mdFile in mdFiles:
    if mdFile == "SUMMARY.md":
        continue

    # # debug
    # if mdFile != "5_2_DCT.md":
    #     continue
    
    newMdFile = re.sub(notionExportNamePattern, "", mdFile)

    with open(mdFile, "r", encoding="utf-8") as f:
        print(f"Parse {mdFile}")
        content = f.read()

    # replace latex formula
    content = re.sub(latexInLinePattern, r"\\\\( \g<1> \\\\)", content)
    content = re.sub(latexInLinePattern, r"\\\\(\\\\( \g<1> \\\\)\\\\)", content)

    # # replace bracket
    # content = re.sub(leftBracketPattern, r"  \(", content)
    # content = re.sub(rightBracketPattern, r"\)  ", content)

    # process image
    # FIXME: 遇到 markdown 两次引用同一张图片时会有问题
    pics = re.findall(picUrlPattern, content)
    picRemoveList = []
    for (idx,pic) in enumerate(pics):
        (picF, picL) = pic
        # print(pic)
        picLDecode = urllib.parse.unquote(picL)
        newPic = f"markdown_images/{newMdFile[:-3]}_{idx}.{picL.split('.')[-1]}"
        # print(newPic)
        if picL == newPic and picF == newPic.split("/")[-1][:-4]:
            continue
        with open(picLDecode, "rb") as f:
            picData = f.read()
        with open(newPic, "wb") as f:
            f.write(picData)
        print(f"Move {picL} to {newPic}")
        # print(content)
        # print(picL)
        # print(re.findall(pic, content))
        # print(re.findall(r"\(\<?"+picL+r"\>?\)", content))
        # print(re.findall(r"\["+picF+r"\]", content))
        content = re.sub(r"\(\<?"+picL+r"\>?\)", f"(<{newPic}>)", content)
        content = re.sub(r"\["+picF+r"\]", f"[{newPic.split('/')[-1][:-4]}]", content)

        
        # print(content)
        picRemoveList.append(picLDecode)
    for pic in set(picRemoveList):
        os.remove(pic)

    # rename markdown file and clear the notion exported dir
    with open(newMdFile, "w", encoding="utf-8") as f:
        f.write(content)
    if newMdFile != mdFile:
        print(f"Move {mdFile} to {newMdFile}")
        os.remove(mdFile)
        if os.path.isdir(mdFile[:-3].split('_')[-1]):
            print(f"Remove {mdFile[:-3].split('_')[-1]} Directory")
            os.removedirs(mdFile[:-3].split('_')[-1])
        else:
            # for debug
            print(f"{mdFile[:-3].split('_')[-1]} is not a dir")
        
    # update summary
    with open("SUMMARY.md", "r", encoding="utf-8") as f:
        content = f.read()
    if newMdFile not in content:
        with open("SUMMARY.md", "a", encoding="utf-8") as f:
            f.write("\n")
            f.write(f"* [{newMdFile[:-3].split('_')[-1]}](<./{newMdFile}>)")
            print(f"add {newMdFile} to SUMMARY")
