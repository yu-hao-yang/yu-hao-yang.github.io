# 艺术明信片

本目录保存当前 18 张成品，全部为 1086 × 1448 像素、竖版 3:4。在网站 Photography 页面可切换查看成品与原始照片。旧版成品与生成记录已清理。

使用 `scripts/build_postcards.py` 统一排版。上半部分直接拼贴经过 EXIF 方向校正的原始 JPG，等比例缩小、完整保留画面；下半部分使用独立保存于 `scripts/postcard_illustrations/` 的透明插画素材。原始 JPG 位于并列的 `../originals/` 目录，文件内容未修改，竖幅照片两侧保留纸色留白。

英文短句统一使用 Apple Chancery，字号 52 px、基线 y=890；底部统一使用 American Typewriter，字号 22 px、基线 y=1392，水平居中 x=543。地点和年月取自文件名。`layout.json` 记录每张图片的排版参数。

在装有 Pillow、NumPy 和上述 macOS 字体的环境运行 `python3 scripts/build_postcards.py` 可重新生成成品；添加 `--only 文件名不含扩展名` 可只生成样张。独立插画素材使脚本不再依赖旧版成品。

网页 Photography 页支持 Original / Postcard 切换，全屏查看时也可切换。图片采用单列居中，原图横幅较宽、竖幅较窄，明信片统一宽度。
