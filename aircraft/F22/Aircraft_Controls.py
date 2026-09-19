# 使用：打开对应的飞机 .blend，在文本编辑器打开本文件，按 Alt+P 运行。
# 回到 3D 视图按 N，打开「Aircraft」标签；滑条定位动画，保留原始缓动。
# 每次重新打开 Blender 后运行一次即可；可重复运行，也可作为插件安装。

bl_info = {
    'name': 'Aircraft · 飞机模型展示控制',
    'author': 'OpenAI',
    'version': (1, 1, 0),
    'blender': (4, 0, 0),
    'location': '3D 视图 > N 侧栏 > Aircraft',
    'description': '装配、爆炸展开、往返动画与展示文字控制',
    'category': '3D View',
}

import bpy
import math

ROOT_NAME = 'EXPLODE • 展开程度 0—1'
TITLE_COLLECTION = '91 · TITLES / 展示标注'
ASSEMBLED_CAMERA = 'CAM 01 · Assembled'
EXPLODED_CAMERA = 'CAM 02 · Exploded'
SLIDER_PROPERTY = 'aircraft_explosion_progress'
TITLES_PROPERTY = 'aircraft_show_titles'
TITLES_STORAGE = '_aircraft_show_titles'


def _controller(scene):
    return scene.objects.get(ROOT_NAME)


def _display_name(scene):
    return str(scene.get('aircraft_display_name', 'Aircraft'))


def _title_collection(scene):
    # Restrict changes to the exact presentation collection in this scene.
    pending = [scene.collection]
    visited = set()
    while pending:
        collection = pending.pop()
        if collection.as_pointer() in visited:
            continue
        visited.add(collection.as_pointer())
        if collection.name == TITLE_COLLECTION:
            return collection
        pending.extend(list(collection.children))
    return None


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


def _get_show_titles(scene):
    return bool(scene.get(TITLES_STORAGE, True))


def _apply_title_visibility(scene):
    titles = _title_collection(scene)
    if titles is None:
        return
    show = _get_show_titles(scene)
    camera = scene.camera
    # Snapshot first: changing visibility can invalidate collection iteration.
    title_objects = list(titles.all_objects)
    titles.hide_render = not show
    titles.hide_viewport = not show
    for obj in title_objects:
        if obj is None:
            continue
        owner = _camera_parent(obj)
        hidden = not show or (owner is not None and owner != camera)
        obj.hide_render = hidden
        obj.hide_viewport = hidden


def _set_show_titles(scene, value):
    # Write to a separate ID property; never assign the RNA property recursively.
    scene[TITLES_STORAGE] = bool(value)
    _apply_title_visibility(scene)
    _redraw()


def _set_camera(scene, name, context=None):
    camera = scene.objects.get(name)
    if camera is None or camera.type != 'CAMERA':
        return False
    scene.camera = camera
    # Camera changes preserve the user's current text visibility selection.
    _apply_title_visibility(scene)
    if context is not None and context.screen:
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces.active
                if space.region_3d:
                    space.region_3d.view_perspective = 'CAMERA'
    _redraw()
    return True


def _get_progress(scene):
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


class AIRCRAFT_OT_assembled(bpy.types.Operator):
    bl_idname = 'aircraft.assembled'
    bl_label = '完整装配'
    bl_description = '定位第 1 帧，切换装配摄像机'

    @classmethod
    def poll(cls, context):
        return _controller(context.scene) is not None

    def execute(self, context):
        _pause(context)
        context.scene.frame_set(1)
        if not _set_camera(context.scene, ASSEMBLED_CAMERA, context):
            self.report({'WARNING'}, '已定位第 1 帧，但未找到装配摄像机')
        return {'FINISHED'}


class AIRCRAFT_OT_exploded(bpy.types.Operator):
    bl_idname = 'aircraft.exploded'
    bl_label = '全部展开'
    bl_description = '定位第 100 帧，切换爆炸视图摄像机'

    @classmethod
    def poll(cls, context):
        return _controller(context.scene) is not None

    def execute(self, context):
        _pause(context)
        context.scene.frame_set(100)
        if not _set_camera(context.scene, EXPLODED_CAMERA, context):
            self.report({'WARNING'}, '已定位第 100 帧，但未找到展开摄像机')
        return {'FINISHED'}


class AIRCRAFT_OT_play_pause(bpy.types.Operator):
    bl_idname = 'aircraft.play_pause'
    bl_label = '播放 / 暂停'
    bl_description = '播放或暂停装配、展开、复原的往返动画'

    @classmethod
    def poll(cls, context):
        return _controller(context.scene) is not None and context.screen is not None

    def execute(self, context):
        if context.screen.is_animation_playing:
            _pause(context)
        else:
            _set_camera(context.scene, EXPLODED_CAMERA, context)
            if context.scene.frame_current >= context.scene.frame_end:
                context.scene.frame_set(context.scene.frame_start)
            if not bpy.ops.screen.animation_play.poll():
                self.report({'WARNING'}, '请在 3D 视图中使用播放按钮')
                return {'CANCELLED'}
            bpy.ops.screen.animation_play()
        _redraw()
        return {'FINISHED'}


class AIRCRAFT_OT_select_controller(bpy.types.Operator):
    bl_idname = 'aircraft.select_controller'
    bl_label = '选中展开控制器'
    bl_description = '选中带有 Explode 动画属性的控制器，保留原始关键帧'

    @classmethod
    def poll(cls, context):
        return _controller(context.scene) is not None

    def execute(self, context):
        obj = _controller(context.scene)
        if context.view_layer.objects.get(obj.name) is None:
            self.report({'WARNING'}, '请先在大纲视图中启用控制器所在集合')
            return {'CANCELLED'}
        if context.object and context.object.mode != 'OBJECT':
            if bpy.ops.object.mode_set.poll():
                bpy.ops.object.mode_set(mode='OBJECT')
        for selected in list(context.selected_objects):
            selected.select_set(False)
        obj.hide_viewport = False
        obj.hide_set(False)
        obj.hide_select = False
        obj.select_set(True)
        context.view_layer.objects.active = obj
        _redraw()
        return {'FINISHED'}


class AIRCRAFT_PT_controls(bpy.types.Panel):
    bl_idname = 'AIRCRAFT_PT_controls'
    bl_label = ''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Aircraft'

    def draw_header(self, context):
        self.layout.label(text=_display_name(context.scene) + ' · 模型展示')

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        root = _controller(scene)
        if root is None:
            layout.label(text='请先打开对应的飞机模型 .blend', icon='INFO')
            return

        row = layout.row(align=True)
        row.scale_y = 1.4
        row.operator('aircraft.assembled', icon='CUBE')
        row.operator('aircraft.exploded', icon='OUTLINER_OB_EMPTY')
        playing = bool(context.screen and context.screen.is_animation_playing)
        row = layout.row()
        row.scale_y = 1.25
        row.operator('aircraft.play_pause', text='暂停动画' if playing else '播放往返动画',
                     icon='PAUSE' if playing else 'PLAY')

        layout.separator()
        layout.prop(scene, SLIDER_PROPERTY, text='展开程度', slider=True)
        layout.label(text='滑条定位第 28–100 帧，保留缓动', icon='TIME')
        layout.prop(scene, TITLES_PROPERTY, text='显示画面文字')
        layout.separator()

        box = layout.box()
        box.label(text='1：完整   100：展开   220：复原')
        box.label(text='当前帧：' + str(scene.frame_current))
        box.label(text='零件展开：{:.0%}'.format(float(root.get('Explode', 0.0))))
        layout.operator('aircraft.select_controller', icon='RESTRICT_SELECT_OFF')


CLASSES = (
    AIRCRAFT_OT_assembled,
    AIRCRAFT_OT_exploded,
    AIRCRAFT_OT_play_pause,
    AIRCRAFT_OT_select_controller,
    AIRCRAFT_PT_controls,
)


def unregister():
    for property_name in (SLIDER_PROPERTY, TITLES_PROPERTY):
        if hasattr(bpy.types.Scene, property_name):
            delattr(bpy.types.Scene, property_name)
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
        description='定位第 28–100 帧的展开动画，保留原有缓动与关键帧',
        min=0.0, max=1.0, subtype='FACTOR', precision=2,
        get=_get_progress, set=_set_progress,
    ))
    setattr(bpy.types.Scene, TITLES_PROPERTY, bpy.props.BoolProperty(
        name='显示画面文字',
        description='同时控制展示文字的视图和渲染可见性，切换视角时保留选择',
        get=_get_show_titles, set=_set_show_titles,
    ))
    for scene in bpy.data.scenes:
        if _controller(scene) is not None:
            _apply_title_visibility(scene)
    _redraw()


if __name__ == '__main__':
    register()
    print('Aircraft 展示控制已就绪：3D 视图 > N 侧栏 > Aircraft')
