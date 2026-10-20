# J-36 · 36011 Blender 外观模型

以首架 36011 的外形构型为基础，仅制作一架飞机。按你提供的三视参考图调整轮廓、座舱位置、深灰几何迷彩和张开的外翼分裂舵面；公开照片用于核对进排气与起落架构型。

本次按新增参考重做尾部融合整流体、后向喷口暗腔和机腹细节；座舱玻璃缩小并压低，机鼻前伸探针已移除。三处喷口增加红橙色尾流、激波亮节与细环效果。

## 文件

- 主文件：`J36_36011_Master.blend`
- 渲染图：`renders/` 内八张 3840 × 2160 PNG，分别为主视角、后视、俯视、前视、细节、侧视、腹部与喷口特写。
- 原始外观参照：`references/`

Blender 5.2 工程，使用 Cycles 渲染。机体、接缝与操纵面、座舱、进排气、起落架、外部标记按集合组织；起落架单独成组，材质可编辑。含八个相机，摄影棚与模型分组。移动 `00 • Aircraft transform` 集合中的根物体可以整体移动飞机。三视图、主要外观参考和 4096 × 4096 迷彩图像已内嵌，无需另装插件。

关闭 `07 • Exhaust effects` 集合的渲染开关，即可关闭全部尾焰与马赫环效果。`08 • Ventral exterior refinements` 为新增腹部外观细节。腹部与喷口特写采用无地面展示，自动出图已配置相应开关。尾焰是按本次要求制作的可选视觉效果，不代表已验证的原型机排气状态或物理模拟结果。

## 精度边界

这是依照用户三视参考图与公开照片制作的视觉模型，不能验证与原型机“100% 一致”。用户提供的是外观绘制参考，未包含测绘尺寸或官方来源；迷彩按该图手工重建，不代表已确认的实机涂装。模型采用的比例尺、不可见面板走线、座舱内部、小型起落架附件及细小紧固件包含建模近似。没有制作可用于工程验证的内部结构。

## 参照来源

- 用户三视参考图：`references/User_Three_View.png`，用于轮廓与涂装。
- 本次补充参考：`references/Revision_Ref_1.png`、`Revision_Ref_3.png`、`Revision_Ref_4.png`、`Revision_Ref_5.png`；无探针机鼻参考为 `Revision_No_Probe.png`。
- [2025-04-23：后部与多角度外观照片](https://www.twz.com/air/new-views-of-chinas-next-generation-fighters)
- [2025-05-31：正面进场照片](https://www.twz.com/air/chinas-j-36-very-heavy-stealth-tactical-jet-photographed-head-on-for-first-time)
- [2025-06-06：正面、腹面及多视角照片；附影像真实性限制](https://www.twz.com/air/this-could-be-our-best-view-yet-of-chinas-j-36-very-heavy-stealth-tactical-jet)

以上网页转载公开流传照片，署名为 Chinese Internet／via X；本项目不将参考插画或推测细节表述为原型机实测数据。
