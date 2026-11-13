# 三维模型与可视化资产：内容索引

盘点日期：2026-11-14。来源：默认分支 main，提交 `f83ae275bb9392be18f0bc0c73ae9bda8aab6365`。

按飞机模型、建筑原模、光储充园区及交付版本分类。首页原先仅突出三款飞机，现补齐园区与建筑入口。

## 分类入口

| 分类 | 入口与内容 |
| --- | --- |
| 飞机模型 | [飞机模型](<../aircraft/>)：F22、J20、Rafale、J36_36011；模型、脚本、预览及说明按机型成套保留。 |
| 建筑原模 | [建筑原模](<../3D Model/Ulaanbaatar_AB_BIPV_DWG_Reconstructed.blend>)：乌兰巴托双塔 CBD 原始 Blender 工程。 |
| 园区 V06 | [园区 V06](<../3D Model/光储充示范园区/README.md>)：分卷 ZIP、清单、还原脚本和字幕。 |
| 园区 V07 | [园区 V07](<../3D Model/光储充示范园区/V07_CBD_整合版/README.md>)：CBD 整合版 Blender、GLB、完整 ZIP 与预览。 |

## 依赖与保留原则

restore.py 以自身位置读取 MANIFEST.json 和分卷；.command 切换到脚本目录。所有分卷、模型、材质引用和脚本保持原位。未打开 Blender、解压大型包或验证二进制内部依赖。

本次不改默认分支，不自动合并、不删除仓库、不将活跃源码标记为停用。目录树未被 GitHub 截断；下列清单覆盖盘点提交的 78 个文件，其中 25 个文本文件已读取。其余文件仅依据路径、类型、大小和 Git blob 标识归类，未声称检查二进制内部内容。未发现 .github/workflows、action.yml/action.yaml 或插件清单文件。

## 逐文件清单

这是盘点提交的清单，不包括本次新增索引。归档后的链接指向新位置；原始路径、大小和 blob SHA 可在 [FILES.json](FILES.json) 查询。

| 分类 | 文件 | 字节 | 内容读取 |
| --- | --- | ---: | --- |
| 版本管理与配置 | [.gitattributes](<../.gitattributes>) | 105 | 已读文本 |
| 版本管理与配置 | [.gitignore](<../.gitignore>) | 69 | 仅元数据 |
| 建筑原模 | [3D Model/Ulaanbaatar_AB_BIPV_DWG_Reconstructed.blend](<../3D Model/Ulaanbaatar_AB_BIPV_DWG_Reconstructed.blend>) | 11682381 | 仅元数据 |
| 园区 / V06 交付 | [3D Model/光储充示范园区/MANIFEST.json](<../3D Model/光储充示范园区/MANIFEST.json>) | 27117 | 已读文本 |
| 园区 / V06 交付 | [3D Model/光储充示范园区/PV_Park_V06_Complete.zip.part001](<../3D Model/光储充示范园区/PV_Park_V06_Complete.zip.part001>) | 41943040 | 仅元数据 |
| 园区 / V06 交付 | [3D Model/光储充示范园区/PV_Park_V06_Complete.zip.part002](<../3D Model/光储充示范园区/PV_Park_V06_Complete.zip.part002>) | 41943040 | 仅元数据 |
| 园区 / V06 交付 | [3D Model/光储充示范园区/PV_Park_V06_Complete.zip.part003](<../3D Model/光储充示范园区/PV_Park_V06_Complete.zip.part003>) | 41943040 | 仅元数据 |
| 园区 / V06 交付 | [3D Model/光储充示范园区/PV_Park_V06_Complete.zip.part004](<../3D Model/光储充示范园区/PV_Park_V06_Complete.zip.part004>) | 41943040 | 仅元数据 |
| 园区 / V06 交付 | [3D Model/光储充示范园区/PV_Park_V06_Complete.zip.part005](<../3D Model/光储充示范园区/PV_Park_V06_Complete.zip.part005>) | 41943040 | 仅元数据 |
| 园区 / V06 交付 | [3D Model/光储充示范园区/PV_Park_V06_Complete.zip.part006](<../3D Model/光储充示范园区/PV_Park_V06_Complete.zip.part006>) | 4162327 | 仅元数据 |
| 园区 / V06 交付 | [3D Model/光储充示范园区/README.md](<../3D Model/光储充示范园区/README.md>) | 2232 | 已读文本 |
| 园区 / V07 | [3D Model/光储充示范园区/V07_CBD_整合版/CBD商业体_整合近景.png](<../3D Model/光储充示范园区/V07_CBD_整合版/CBD商业体_整合近景.png>) | 2642104 | 仅元数据 |
| 园区 / V07 | [3D Model/光储充示范园区/V07_CBD_整合版/README.md](<../3D Model/光储充示范园区/V07_CBD_整合版/README.md>) | 1142 | 已读文本 |
| 园区 / V07 | [3D Model/光储充示范园区/V07_CBD_整合版/V07园区全景.png](<../3D Model/光储充示范园区/V07_CBD_整合版/V07园区全景.png>) | 3266049 | 仅元数据 |
| 园区 / V07 | [3D Model/光储充示范园区/V07_CBD_整合版/park.glb](<../3D Model/光储充示范园区/V07_CBD_整合版/park.glb>) | 4616640 | 仅元数据 |
| 园区 / V07 | [3D Model/光储充示范园区/V07_CBD_整合版/pv_park_500mu_v07.blend](<../3D Model/光储充示范园区/V07_CBD_整合版/pv_park_500mu_v07.blend>) | 11964498 | 仅元数据 |
| 园区 / V07 | [3D Model/光储充示范园区/V07_CBD_整合版/光储充示范园区_V07_CBD整合.zip](<../3D Model/光储充示范园区/V07_CBD_整合版/光储充示范园区_V07_CBD整合.zip>) | 56464529 | 仅元数据 |
| 园区 / V06 交付 | [3D Model/光储充示范园区/restore.py](<../3D Model/光储充示范园区/restore.py>) | 1674 | 已读文本 |
| 园区 / V06 交付 | [3D Model/光储充示范园区/云浏览字幕.srt](<../3D Model/光储充示范园区/云浏览字幕.srt>) | 1636 | 仅元数据 |
| 园区 / V06 交付 | [3D Model/光储充示范园区/合并解压.command](<../3D Model/光储充示范园区/合并解压.command>) | 136 | 已读文本 |
| 园区 / V06 交付 | [3D Model/光储充示范园区/项目需求提示词.md](<../3D Model/光储充示范园区/项目需求提示词.md>) | 5739 | 已读文本 |
| 园区 / V06 交付 | [3D Model/光储充示范园区/预览.png](<../3D Model/光储充示范园区/预览.png>) | 2311375 | 仅元数据 |
| 仓库说明 | [README.md](<../README.md>) | 3373 | 已读文本 |
| 飞机模型 / F22 | [aircraft/F22/Aircraft_Controls.py](<../aircraft/F22/Aircraft_Controls.py>) | 10757 | 已读文本 |
| 飞机模型 / F22 | [aircraft/F22/F22_01_Assembled.png](<../aircraft/F22/F22_01_Assembled.png>) | 6445908 | 仅元数据 |
| 飞机模型 / F22 | [aircraft/F22/F22_02_Exploded.png](<../aircraft/F22/F22_02_Exploded.png>) | 6651288 | 仅元数据 |
| 飞机模型 / F22 | [aircraft/F22/F22_03_Rear.png](<../aircraft/F22/F22_03_Rear.png>) | 6395596 | 仅元数据 |
| 飞机模型 / F22 | [aircraft/F22/F22_Explode_Animation.mp4](<../aircraft/F22/F22_Explode_Animation.mp4>) | 1143846 | 仅元数据 |
| 飞机模型 / F22 | [aircraft/F22/F22_Modular.blend](<../aircraft/F22/F22_Modular.blend>) | 1620930 | 仅元数据 |
| 飞机模型 / F22 | [aircraft/F22/使用说明.txt](<../aircraft/F22/使用说明.txt>) | 2229 | 已读文本 |
| 飞机模型 / J20 | [aircraft/J20/J20_01_Assembled.png](<../aircraft/J20/J20_01_Assembled.png>) | 6369261 | 仅元数据 |
| 飞机模型 / J20 | [aircraft/J20/J20_02_Exploded.png](<../aircraft/J20/J20_02_Exploded.png>) | 6572109 | 仅元数据 |
| 飞机模型 / J20 | [aircraft/J20/J20_03_Rear.png](<../aircraft/J20/J20_03_Rear.png>) | 6379735 | 仅元数据 |
| 飞机模型 / J20 | [aircraft/J20/J20_Controls.py](<../aircraft/J20/J20_Controls.py>) | 9227 | 已读文本 |
| 飞机模型 / J20 | [aircraft/J20/J20_Explode_Animation.mp4](<../aircraft/J20/J20_Explode_Animation.mp4>) | 1017767 | 仅元数据 |
| 飞机模型 / J20 | [aircraft/J20/J20_Modular.blend](<../aircraft/J20/J20_Modular.blend>) | 1487681 | 仅元数据 |
| 飞机模型 / J20 | [aircraft/J20/使用说明.txt](<../aircraft/J20/使用说明.txt>) | 2495 | 已读文本 |
| 版本管理与配置 | [aircraft/J36_36011/.gitignore](<../aircraft/J36_36011/.gitignore>) | 54 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/DELIVERY.md](<../aircraft/J36_36011/DELIVERY.md>) | 2824 | 已读文本 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/J36_36011_Master.blend](<../aircraft/J36_36011/J36_36011_Master.blend>) | 8485468 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/README.md](<../aircraft/J36_36011/README.md>) | 2167 | 已读文本 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/model_stats.json](<../aircraft/J36_36011/model_stats.json>) | 129 | 已读文本 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/references/Revision_No_Probe.png](<../aircraft/J36_36011/references/Revision_No_Probe.png>) | 722607 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/references/Revision_Ref_1.png](<../aircraft/J36_36011/references/Revision_Ref_1.png>) | 758634 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/references/Revision_Ref_2.png](<../aircraft/J36_36011/references/Revision_Ref_2.png>) | 1706529 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/references/Revision_Ref_3.png](<../aircraft/J36_36011/references/Revision_Ref_3.png>) | 633785 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/references/Revision_Ref_4.png](<../aircraft/J36_36011/references/Revision_Ref_4.png>) | 328251 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/references/Revision_Ref_5.png](<../aircraft/J36_36011/references/Revision_Ref_5.png>) | 420156 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/references/User_Three_View.png](<../aircraft/J36_36011/references/User_Three_View.png>) | 453398 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/references/composite.jpg](<../aircraft/J36_36011/references/composite.jpg>) | 163466 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/references/front.jpg](<../aircraft/J36_36011/references/front.jpg>) | 292276 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/references/front_close.jpg](<../aircraft/J36_36011/references/front_close.jpg>) | 383738 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/references/rear.jpg](<../aircraft/J36_36011/references/rear.jpg>) | 47363 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/references/underside.jpg](<../aircraft/J36_36011/references/underside.jpg>) | 43641 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/references/underside_close.jpg](<../aircraft/J36_36011/references/underside_close.jpg>) | 102062 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/renders/J36_36011_Detail_4K.png](<../aircraft/J36_36011/renders/J36_36011_Detail_4K.png>) | 29519975 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/renders/J36_36011_Exhaust_4K.png](<../aircraft/J36_36011/renders/J36_36011_Exhaust_4K.png>) | 15577390 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/renders/J36_36011_Front_4K.png](<../aircraft/J36_36011/renders/J36_36011_Front_4K.png>) | 23324153 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/renders/J36_36011_Hero_4K.png](<../aircraft/J36_36011/renders/J36_36011_Hero_4K.png>) | 23824478 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/renders/J36_36011_Rear_4K.png](<../aircraft/J36_36011/renders/J36_36011_Rear_4K.png>) | 25646217 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/renders/J36_36011_Side_4K.png](<../aircraft/J36_36011/renders/J36_36011_Side_4K.png>) | 13304558 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/renders/J36_36011_Top_4K.png](<../aircraft/J36_36011/renders/J36_36011_Top_4K.png>) | 26024667 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/renders/J36_36011_Ventral_4K.png](<../aircraft/J36_36011/renders/J36_36011_Ventral_4K.png>) | 8224127 | 仅元数据 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/scripts/build_j36.py](<../aircraft/J36_36011/scripts/build_j36.py>) | 34269 | 已读文本 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/scripts/camouflage.py](<../aircraft/J36_36011/scripts/camouflage.py>) | 7271 | 已读文本 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/scripts/exhaust_fx.py](<../aircraft/J36_36011/scripts/exhaust_fx.py>) | 8022 | 已读文本 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/scripts/gear.py](<../aircraft/J36_36011/scripts/gear.py>) | 13516 | 已读文本 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/scripts/render_views.py](<../aircraft/J36_36011/scripts/render_views.py>) | 2260 | 已读文本 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/scripts/ventral_detail.py](<../aircraft/J36_36011/scripts/ventral_detail.py>) | 5357 | 已读文本 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/scripts/verify_delivery.py](<../aircraft/J36_36011/scripts/verify_delivery.py>) | 3274 | 已读文本 |
| 飞机模型 / J36_36011 | [aircraft/J36_36011/verification.json](<../aircraft/J36_36011/verification.json>) | 2753 | 已读文本 |
| 飞机模型 / Rafale | [aircraft/Rafale/Aircraft_Controls.py](<../aircraft/Rafale/Aircraft_Controls.py>) | 10757 | 已读文本 |
| 飞机模型 / Rafale | [aircraft/Rafale/Rafale_01_Assembled.png](<../aircraft/Rafale/Rafale_01_Assembled.png>) | 6296383 | 仅元数据 |
| 飞机模型 / Rafale | [aircraft/Rafale/Rafale_02_Exploded.png](<../aircraft/Rafale/Rafale_02_Exploded.png>) | 6572956 | 仅元数据 |
| 飞机模型 / Rafale | [aircraft/Rafale/Rafale_03_Rear.png](<../aircraft/Rafale/Rafale_03_Rear.png>) | 6319974 | 仅元数据 |
| 飞机模型 / Rafale | [aircraft/Rafale/Rafale_Explode_Animation.mp4](<../aircraft/Rafale/Rafale_Explode_Animation.mp4>) | 1119156 | 仅元数据 |
| 飞机模型 / Rafale | [aircraft/Rafale/Rafale_Modular.blend](<../aircraft/Rafale/Rafale_Modular.blend>) | 1310285 | 仅元数据 |
| 飞机模型 / Rafale | [aircraft/Rafale/使用说明.txt](<../aircraft/Rafale/使用说明.txt>) | 2160 | 已读文本 |
