import re
import os
import glob
import urllib.parse

mdFilePaths = glob.glob("docs/**/*.md", recursive=True)
print(mdFilePaths)
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

    
    newMdFile = re.sub(notionExportNamePattern, "", mdFile)

    with open(mdFilePath, "r", encoding="utf-8") as f:
        print(f"Parse {mdFile}")
        content = f.read()

#     # # replace latex formula
#     # content = re.sub(latexInLinePattern, r"\\\\( \g<1> \\\\)", content)
#     # content = re.sub(latexInLinePattern, r"\\\\(\\\\( \g<1> \\\\)\\\\)", content)

#     # # replace bracket
#     # content = re.sub(leftBracketPattern, r"  \(", content)
#     # content = re.sub(rightBracketPattern, r"\)  ", content)

    # process image
    # FIXME: 遇到 markdown 两次引用同一张图片时会有问题
    pics = re.findall(picUrlPattern, content)
    picRemoveList = []
    for (idx,pic) in enumerate(pics):
        (picF, picL) = pic
        # print(pic)
        picLDecode = urllib.parse.unquote(picL)
        newPic = f"markdown_images/{newMdFile[:-3]}_{idx}.{picL.split('.')[-1]}"
        newPicEncode = urllib.parse.quote(newPic)
        # print(newPic)
        if picL == newPicEncode and picF == newPic.split("/")[-1][:-4]:
            continue
        with open(os.path.join(mdFileDir, picLDecode), "rb") as f:
            picData = f.read()
        with open(os.path.join(mdFileDir, newPic), "wb") as f:
            f.write(picData)
        print(f"Move {picL} to {newPic}")
        # print(content)
        # print(picL)
        # print(re.findall(pic, content))
        # print(re.findall(r"\(\<?"+picL+r"\>?\)", content))
        # print(re.findall(r"\["+picF+r"\]", content))
        content = re.sub(r"\(\<?"+picL+r"\>?\)", f"(<{newPicEncode}>)", content)
        content = re.sub(r"\["+picF+r"\]", f"[{newPic.split('/')[-1][:-4]}]", content)

        
        # print(content)
        picRemoveList.append(picLDecode)
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
    if newMdFile not in content:
        with open("_sidebar.md", "a", encoding="utf-8") as f:
            f.write("\n")
            f.write(f"* [{newMdFile[:-3].split('_')[-1]}](<{os.path.join(mdFileDir, newMdFile)}>)")
            print(f"add {newMdFile} to SUMMARY")
