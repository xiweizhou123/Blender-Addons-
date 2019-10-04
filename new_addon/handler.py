import bpy


event = bpy.types.Event

count = 0


def handle_event(event):
    
    x = event(mouse_region_x)
    y = event(mouse_region_y)
    if(event.type == 'LEFTMOUSE'):
        if(event.value == 'PRESS'):
            print(x,y)
 

def my_handler(scene):
    print("Frame Change", scene.frame_current)
    

def do(scene):
    global count 
    count += 1
    print(count)
    handle_event(event)

  
def delete_frame_change_handler():
    for i in bpy.app.handlers.frame_change_pre:
        if i.__name__ ==  'my_handler':
            bpy.app.handlers.frame_change_pre.remove(i)

def delete_scene_change_handler():
    for i in bpy.app.handlers.frame_change_pre:
        if i.__name__ ==  'do':
            bpy.app.handlers.frame_change_pre.remove(i)
            
def add_frame_change_handler(handler):
    bpy.app.handlers.frame_change_pre.append(handler)
        
def add_scene_change_handler(handler):
    bpy.app.handlers.depsgraph_update_pre.append(handler)

#add_frame_change_handler(my_handler)
add_scene_change_handler(do)
delete_frame_change_handler()

'''
scene = bpy.data.scenes['Scene']

def do2(scene):
    print("hello")


class HandlerManager:
    
    def __init__(self):
        self.count = 0
    
    def do(self):
        
        self.count += 1 
        print(count)
    
    def my_handler(scene):
        self.do()
    
    
    def add_handler(my_handler):
        pass
    
bpy.app.handlers.depsgraph_update_pre(do2)
'''