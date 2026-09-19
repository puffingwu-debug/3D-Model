# 使用：先打开 J20_Modular.blend，在文本编辑器打开本文件，按 Alt+P 运行。
# 回到 3D 视图按 N，打开右侧「J20」标签；滑条定位展开动画，不改动关键帧。
# 每次重新打开 Blender 后运行一次即可；可重复运行，也可作为插件安装。

bl_info = {
    'name': 'J20 模型展示控制',
    'author': 'OpenAI',
    'version': (1, 0, 0),
    'blender': (4, 0, 0),
    'location': '3D 视图 > N 侧栏 > J20',
    'description': '完整装配、爆炸展开和往返动画的简明控制面板',
    'category': '3D View',
}

import bpy
import math

ROOT_NAME = 'EXPLODE • 展开程度 0—1'
TITLE_COLLECTION = '91 · TITLES / 展示标注'
ASSEMBLED_CAMERA = 'CAM 01 · Assembled'
EXPLODED_CAMERA = 'CAM 02 · Exploded'
SLIDER_PROPERTY = 'j20_explosion_progress'


def _controller(scene):
    return scene.objects.get(ROOT_NAME)


def _redraw():
    wm = bpy.context.window_manager
    if wm:
        for window in wm.windows:
            for area in window.screen.areas:
                if area.type in {'VIEW_3D', 'DOPESHEET_EDITOR', 'PROPERTIES'}:
                    area.tag_redraw()


def _pause(context):
    screen = context.screen
    if screen and screen.is_animation_playing:
        if bpy.ops.screen.animation_cancel.poll():
            bpy.ops.screen.animation_cancel(restore_frame=False)


def _camera_parent(obj):
    parent = obj.parent
    while parent:
        if parent.type == 'CAMERA':
            return parent
        parent = parent.parent
    return None


def _set_camera(scene, name, context=None):
    camera = scene.objects.get(name)
    if camera is None or camera.type != 'CAMERA':
        return False
    scene.camera = camera
    titles = bpy.data.collections.get(TITLE_COLLECTION)
    if titles:
        for obj in list(titles.all_objects):
            if obj is None or obj.type != 'FONT':
                continue
            owner = _camera_parent(obj)
            if owner is not None:
                hidden = owner != camera
                obj.hide_render = hidden
                obj.hide_viewport = hidden
    # Viewport camera mode makes the selected presentation immediately visible.
    if context is not None and context.screen:
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces.active
                if space.region_3d:
                    space.region_3d.view_perspective = 'CAMERA'
    _redraw()
    return True


def _get_progress(scene):
    # The getter also follows ordinary timeline playback without frame handlers.
    frame = scene.frame_current + scene.frame_subframe
    if frame <= 28:
        return 0.0
    if frame <= 100:
        return (frame - 28.0) / 72.0
    if frame <= 136:
        return 1.0
    if frame < 220:
        return (220.0 - frame) / 84.0
    return 0.0


def _set_progress(scene, value):
    if _controller(scene) is None:
        return
    value = max(0.0, min(1.0, float(value)))
    context = bpy.context
    _pause(context)
    target = 28.0 + value * 72.0
    frame = int(math.floor(target))
    scene.frame_set(frame, subframe=target - frame)
    _set_camera(scene, ASSEMBLED_CAMERA if value <= 0.0001 else EXPLODED_CAMERA,
                context if context.scene == scene else None)


class J20_OT_assembled(bpy.types.Operator):
    bl_idname = 'j20.assembled'
    bl_label = '完整装配'
    bl_description = '定位第 1 帧，切换装配摄像机和对应展示文字'

    @classmethod
    def poll(cls, context):
        return _controller(context.scene) is not None

    def execute(self, context):
        _pause(context)
        context.scene.frame_set(1)
        if not _set_camera(context.scene, ASSEMBLED_CAMERA, context):
            self.report({'WARNING'}, '已定位第 1 帧，但未找到装配摄像机')
        return {'FINISHED'}


class J20_OT_exploded(bpy.types.Operator):
    bl_idname = 'j20.exploded'
    bl_label = '全部展开'
    bl_description = '定位第 100 帧，切换爆炸视图摄像机和对应展示文字'

    @classmethod
    def poll(cls, context):
        return _controller(context.scene) is not None

    def execute(self, context):
        _pause(context)
        context.scene.frame_set(100)
        if not _set_camera(context.scene, EXPLODED_CAMERA, context):
            self.report({'WARNING'}, '已定位第 100 帧，但未找到展开摄像机')
        return {'FINISHED'}


class J20_OT_play_pause(bpy.types.Operator):
    bl_idname = 'j20.play_pause'
    bl_label = '播放 / 暂停'
    bl_description = '播放或暂停完整装配、展开、复原的往返动画'

    @classmethod
    def poll(cls, context):
        return _controller(context.scene) is not None and context.screen is not None

    def execute(self, context):
        if context.screen.is_animation_playing:
            _pause(context)
        else:
            # The wide camera retains every detached component in the shot.
            _set_camera(context.scene, EXPLODED_CAMERA, context)
            if context.scene.frame_current >= context.scene.frame_end:
                context.scene.frame_set(context.scene.frame_start)
            if not bpy.ops.screen.animation_play.poll():
                self.report({'WARNING'}, '请在 3D 视图中使用播放按钮')
                return {'CANCELLED'}
            bpy.ops.screen.animation_play()
        _redraw()
        return {'FINISHED'}


class J20_OT_select_controller(bpy.types.Operator):
    bl_idname = 'j20.select_controller'
    bl_label = '选中展开控制器'
    bl_description = '选中带有 Explode 动画属性的控制器，保留全部原始关键帧'

    @classmethod
    def poll(cls, context):
        return _controller(context.scene) is not None

    def execute(self, context):
        obj = _controller(context.scene)
        if context.view_layer.objects.get(obj.name) is None:
            self.report({'WARNING'}, '控制器所在集合被排除，请先在大纲视图中启用集合')
            return {'CANCELLED'}
        if context.object and context.object.mode != 'OBJECT':
            if bpy.ops.object.mode_set.poll():
                bpy.ops.object.mode_set(mode='OBJECT')
        for selected in context.selected_objects:
            selected.select_set(False)
        obj.hide_viewport = False
        obj.hide_set(False)
        obj.hide_select = False
        obj.select_set(True)
        context.view_layer.objects.active = obj
        _redraw()
        return {'FINISHED'}


class J20_PT_controls(bpy.types.Panel):
    bl_idname = 'J20_PT_controls'
    bl_label = 'J-20 · 模型展示'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'J20'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        root = _controller(scene)
        if root is None:
            layout.label(text='请先打开 J20_Modular.blend', icon='INFO')
            return

        row = layout.row(align=True)
        row.scale_y = 1.4
        row.operator('j20.assembled', icon='CUBE')
        row.operator('j20.exploded', icon='OUTLINER_OB_EMPTY')
        playing = bool(context.screen and context.screen.is_animation_playing)
        row = layout.row()
        row.scale_y = 1.25
        row.operator('j20.play_pause', text='暂停动画' if playing else '播放往返动画',
                     icon='PAUSE' if playing else 'PLAY')

        layout.separator()
        layout.prop(scene, SLIDER_PROPERTY, text='展开程度', slider=True)
        layout.label(text='滑条定位展开段：第 28–100 帧', icon='TIME')
        layout.label(text='原始动画关键帧全部保留')
        layout.separator()

        box = layout.box()
        box.label(text='1：完整   100：展开   220：复原')
        box.label(text='当前帧：' + str(scene.frame_current))
        amount = float(root.get('Explode', 0.0))
        box.label(text='零件展开：{:.0%}'.format(amount))
        layout.operator('j20.select_controller', icon='RESTRICT_SELECT_OFF')


CLASSES = (
    J20_OT_assembled,
    J20_OT_exploded,
    J20_OT_play_pause,
    J20_OT_select_controller,
    J20_PT_controls,
)


def unregister():
    if hasattr(bpy.types.Scene, SLIDER_PROPERTY):
        delattr(bpy.types.Scene, SLIDER_PROPERTY)
    # Find registered RNA types, including classes from a previous Alt+P run.
    for cls in reversed(CLASSES):
        previous = getattr(bpy.types, cls.__name__, None)
        if previous is not None:
            try:
                bpy.utils.unregister_class(previous)
            except (RuntimeError, ValueError):
                pass


def register():
    unregister()
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    setattr(bpy.types.Scene, SLIDER_PROPERTY, bpy.props.FloatProperty(
        name='展开程度',
        description='定位第 28–100 帧的展开动画；保留原有缓动与关键帧',
        min=0.0,
        max=1.0,
        subtype='FACTOR',
        precision=2,
        get=_get_progress,
        set=_set_progress,
    ))
    _redraw()


if __name__ == '__main__':
    register()
    print('J20 展示控制已就绪：3D 视图 > N 侧栏 > J20')
