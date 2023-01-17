import re
import os
import sys
import glob
import random
import urllib.parse
import hashlib

def getMdFiles(partName):
    ''' 获取需要处理的 MD 文件 '''
    mdFilePaths = glob.glob(f"docs\\{partName}\\**\\*.md", recursive=True)

    # for debug
    print()
    print(f"partName:{partName}")
    print(f"待处理的 md 文件:{mdFilePaths}")

    return mdFilePaths

def parseMdFiles(partName, mdFilePaths):
    ''' 处理输入的 MD 文件 '''

    # regex pattern
    latexInLinePattern = r"\$([^\$]+)\$"
    latexBlockPattern = r"\$\$([^\$]+)\$\$"
    picUrlPattern = r"!\[(.*)\]\(<?([^<^>]+?)>?\)"
    notionExportNamePattern = r" [a-z0-9]{32}"
    leftBracketPattern = r"（"
    rightBracketPattern = r"）"

    # 逐个处理文件
    for mdFilePath in mdFilePaths:
        mdFile = os.path.basename(mdFilePath)
        mdFileDir = os.path.dirname(mdFilePath)
        if mdFile == "_sidebar.md" or mdFile == "README.md":
            continue

        stdMdFile = re.sub(notionExportNamePattern, "", mdFile).replace(" ","_")

        with open(mdFilePath, "r", encoding="utf-8") as f:
            print(f"Parse {mdFile}")
            content = f.read()

        # process image
        # FIXME: 遇到 markdown 两次引用同一张图片时会有问题
        # 目的1：保证图片前缀为 md 文件名，后缀为图片内容的 hash 值 % 1e7
        # 目的2：删除多余没有被任何 md 文件引用的图片
        if not os.path.isdir(os.path.join(mdFileDir, "markdown_images")):
            os.mkdir(os.path.join(mdFileDir, "markdown_images"))
        pics = re.findall(picUrlPattern, content)
        picRemoveList = []
        for (idx,pic) in enumerate(pics):
            # 例子：![编解码流程_6379](markdown_images/%E7%BC%96%E8%A7%A3%E7%A0%81%E6%B5%81%E7%A8%8B_6379.png)
            # picName: 编解码流程_6379
            # picPath: markdown_images/%E7%BC%96%E8%A7%A3%E7%A0%81%E6%B5%81%E7%A8%8B_6379.png
            (picName, picPath) = pic

            picPathDecode = urllib.parse.unquote(picPath)

            with open(os.path.join(mdFileDir, picPathDecode), "rb") as f:
                picData = f.read()

            # 获取图片内容的 hash 值作为图片文件名，得到 stdPicPath 初始值
            hash_num = int(int(hashlib.md5(picData).hexdigest(), 16) % 1e10)
            stdPicPath = f"markdown_images/{stdMdFile[:-3]}_{hash_num}.{picPathDecode.split('.')[-1]}"

            # 若图片文件名符合要求，则此轮循环结束
            if picPathDecode.startswith(stdPicPath.split('.')[0]) and picPathDecode.endswith(stdPicPath.split('.')[1]):
                continue

            # for debug
            # print(f"{picPathDecode} != {stdPicPath}")

            # 获取最终的 stdPicPath
            # i = 0
            # while os.path.isfile(os.path.join(mdFileDir, stdPicPath)):
            #     i = i + 1
            #     stdPicPath = f"markdown_images/{stdMdFile[:-3]}_{hash_num}_{i}.{picPathDecode.split('.')[-1]}"
            stdPicPathEncode = urllib.parse.quote(stdPicPath)

            # stdPicName
            stdPicName = os.path.basename(stdPicPath).split(".")[0]

            with open(os.path.join(mdFileDir, stdPicPath), "wb") as f:
                f.write(picData)

            print(f"Move {picPathDecode} to {stdPicPath}")

            content = re.sub(r"\(\<?"+picPath+r"\>?\)", f"({stdPicPathEncode})", content)
            content = re.sub(r"\["+picName+r"\]", f"[{stdPicName}]", content)

        # rename markdown file and clear the notion exported dir
        with open(os.path.join(mdFileDir, stdMdFile), "w", encoding="utf-8") as f:
            f.write(content)
        if stdMdFile != mdFile:
            print(f"Move {mdFile} to {stdMdFile}")
            os.remove(mdFilePath)
            # notionImagePath = os.path.join(mdFileDir, mdFile[:-3].split('_')[-1])
            # if os.path.isdir(notionImagePath):
            #     print(f"Remove {notionImagePath} Directory")
            #     os.removedirs(notionImagePath)
            # else:
            #     # for debug
            #     print(f"{notionImagePath} is not a dir")
        
        # update sidebar
        if not os.path.isfile(f"docs/{partName}/_sidebar.md"):
            with open(f"docs/{partName}/_sidebar.md", "w", encoding="utf-8") as f:
                f.write("\n")
                f.write(f"* [{stdMdFile[:-3].replace('_', ' ')}](<./{os.path.join(mdFileDir, stdMdFile)}>)".replace('\\','/'))
                print(f"create docs/{partName}/_sidebar.md")
                print(f"add {stdMdFile} to sidebar")
        else:
            with open(f"docs/{partName}/_sidebar.md", "r", encoding="utf-8") as f:
                content = f.read()
            if os.path.join(mdFileDir, stdMdFile).replace('\\','/') not in content:
                # print(os.path.join(mdFileDir, stdMdFile))
                with open(f"docs/{partName}/_sidebar.md", "a", encoding="utf-8") as f:
                    f.write("\n")
                    f.write(f"* [{stdMdFile[:-3].replace('_', ' ')}](<./{os.path.join(mdFileDir, stdMdFile)}>)".replace('\\','/'))
                    print(f"add {stdMdFile} to sidebar")

def clearRedundantResource():
    ''' 清除无引用的图片和空文件夹 '''
    print()
    # 删除无引用的图片
    print("开始清理冗余图片")
    imgFilePaths = glob.glob("docs/**/*.png", recursive=True)
    for imgFilePath in imgFilePaths:
        imgFileNameEnecode = urllib.parse.quote(os.path.basename(imgFilePath))
        mdFilePaths = glob.glob(os.path.dirname(imgFilePath)+"\\..\\*.md")

        # for debug
        # print(f"imgFilePath={imgFilePath}, search {mdFilePaths}")

        for mdFilePath in mdFilePaths:
            with open(mdFilePath, "r", encoding="utf-8") as f:
                content = f.read()
            if imgFileNameEnecode in content:
                break
        else:
            print(f"remove redundant image {imgFilePath}")
            os.remove(imgFilePath)

    # 删除空文件夹
    print("开始清理空文件夹")
    files = glob.glob("docs/**/*", recursive=True)
    for file_ in files:
        if os.path.isdir(file_) and (not os.listdir(file_)):
            os.rmdir(file_)
            print(f"remove empty directory {file_}")

def main():
    # if len(sys.argv) < 2:
    #     partNames = [i for i in os.listdir("docs\\") if os.path.isdir(f"docs\\{i}")]
    # else:
    #     partNames = sys.argv[1:]

    # for partName in partNames:
    #     mdFilePaths = getMdFiles(partName)
    #     parseMdFiles(partName, mdFilePaths)
    
    clearRedundantResource()

if __name__ == '__main__':
    main()