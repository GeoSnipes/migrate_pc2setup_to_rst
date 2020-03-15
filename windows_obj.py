import pywinauto as wind
from pywinauto.application import Application
import pyautogui as gui
import path_location
import time

import ocr

def click_here(x=None, y=None, pause=None, debug=False):
    gui.moveTo(x, y, pause=pause)
    if debug:
        gui.press('ctrl', presses=2, interval=.7)
    gui.click()

class Windows:
    def __init__(self):
        self.app = None

    def get_app_prop(self):
        app_prop = self.app.rectangle()
        return (app_prop.left, app_prop.top, app_prop.width(), app_prop.height())

    def get_app_prop2(self):
        app_prop = self.app.client_rect()
        return app_prop.width(), app_prop.height()

    def app_get_region(self, x, y, width=10, height=10, use_ratio=False, draw_outline=True):
        # PCARS 2 options change based on windows size (resolution)
        if use_ratio:
            app_h = self.app.client_rect().height()
            app_w = self.app.client_rect().width()
            x = x * app_w/1768
            y = y * app_h/992
            width = width * app_w/1768
            height = height * app_h/992
        x,y,width,height = int(x),int(y),int(width),int(height)
        x, y = self.app.client_to_screen((x,y))
        
        if draw_outline:
            class cusrect:
                left=x
                top=y
                right=left+width
                bottom=top+height

            for _ in range(25):
                self.app.draw_outline(rect=cusrect)
        return x, y, width, height

    @staticmethod
    def get_screenshot(wind_stat=None, screenname=None):
        if screenname is not None:
            screenname = 'screenshots/'+screenname
            if not screenname.endswith('.png'):
                screenname+='.png'
        else:
            screenname = str(time.time())+'.png'

        if wind_stat == None:
            print('[ERROR] Either app object or custom box has to be passed')
            return None
        return gui.screenshot(imageFilename=screenname, region=wind_stat)
    

class PC2(Windows):
    def __init__(self):
        try:
            self.app = Application().connect(title_re='.*Project CARS 2.*')['Project Cars 2']
        except wind.findwindows.ElementNotFoundError:
            print('[ERROR] Launch PCARS 2 first')
    
    def get_stats_gear_pc2(self):
        # Select ECU menu
        self.app.set_focus()
        pos = self.app_get_region(x=int(self.get_app_prop2()[0]/2)+250, y=250, use_ratio=True)
        click_here(pos[0], pos[1])

        x, y, width, height = self.app_get_region(x=949, y=520,  width=70, height=210, use_ratio=True)
        content = ocr.image_convert(self.get_screenshot(wind_stat=(x, y, width, height), screenname='Gear.png'))
        return ocr.retriev_ocr(content)[0]

    def get_stats_sus_pc2(self):
        # Select suspension menu
        self.app.set_focus()
        pos = self.app_get_region(x=int(self.get_app_prop2()[0]/2)-200, y=250, use_ratio=True)
        click_here(pos[0], pos[1])

        # Get front spring
        x, y, width, height = self.app_get_region(x=600, y=497,  width=90, height=23, use_ratio=True)
        content = ocr.image_convert(self.get_screenshot(wind_stat=(x, y, width, height), screenname='sus_front_spring'))
        f_spring = ocr.retriev_ocr(content)[0]

        # Get rear spring
        x, y, width, height = self.app_get_region(x=600, y=737,  width=90, height=23, use_ratio=True)
        content = ocr.image_convert(self.get_screenshot(wind_stat=(x, y, width, height), screenname='sus_rear_spring.png'))
        r_spring = ocr.retriev_ocr(content)[0]
        
        # Get front antirollbar
        x, y, width, height = self.app_get_region(x=935, y=470,  width=90, height=26, use_ratio=True)
        content = ocr.image_convert(self.get_screenshot(wind_stat=(x, y, width, height), screenname='sus_front_arb.png'))
        f_ar = ocr.retriev_ocr(content)[0]
        
        # Get rear antirollbar
        x, y, width, height = self.app_get_region(x=935, y=710,  width=90, height=26, use_ratio=True)
        content = ocr.image_convert(self.get_screenshot(wind_stat=(x, y, width, height), screenname='sus_rear_arb.png'))
        r_ar = ocr.retriev_ocr(content)[0]
        
        return f_spring, r_spring, f_ar, r_ar

    def get_stats_damp_pc2(self):
        # Select dampers menu
        self.app.set_focus()
        pos = self.app_get_region(x=int(self.get_app_prop2()[0]/2), y=250, use_ratio=True)
        gui.click(pos[0], pos[1])

        # Get front damp
        x, y, width, height = self.app_get_region(x=595, y=445,  width=95, height=105, use_ratio=True)
        content = ocr.image_convert(self.get_screenshot(wind_stat=(x, y, width, height), screenname='sus_front_damp'))
        f_damp = ocr.retriev_ocr(content)

        # Get rear damp
        x, y, width, height = self.app_get_region(x=595, y=710,  width=95, height=105, use_ratio=True)
        content = ocr.image_convert(self.get_screenshot(wind_stat=(x, y, width, height), screenname='sus_rear_damp'))
        r_damp = ocr.retriev_ocr(content)
        
        return f_damp, r_damp

class RST(Windows):
    def __init__(self):
        try:
            self.app = Application().connect(title_re='MainWindow').MainWindow
        except wind.findwindows.ElementNotFoundError:
            RST_LOCATION = path_location.RST_LOCATION

            if RST_LOCATION is None:
                print('Path to RST cannot be found')
                quit()
            self.app = Application().start(RST_LOCATION+'\\RST Software.exe').MainWindow
        except wind.findwindows.ElementAmbiguousError:
            print('[ERROR] Sad, but for now, close the params child window.')

    def open_rst_params(self):
        self.app.set_focus()
        self.app.set_focus()
        RST_FILE_OFFSET_X = 350
        RST_FILE_OFFSET_Y = 10
        RST_NEXT_OFFSET_X = RST_FILE_OFFSET_X+10
        RST_NEXT_OFFSET_Y = RST_FILE_OFFSET_Y+75

        #Select file
        x, y, width, height = self.app_get_region(RST_FILE_OFFSET_X, RST_FILE_OFFSET_Y, 60, 40, draw_outline=True)
        click_here(x=x+width/2, y=y+height/2, pause=0.5)
        
        #Select next car parameters
        x, y, width, height = self.app_get_region(RST_NEXT_OFFSET_X, RST_NEXT_OFFSET_Y, 280, 30, draw_outline=True)
        click_here(x=x+width/2, y=y+height/2, pause=0.5)

    def open_rst_settings(self, settings):
        def find_rst_settings(pos):
            setup_bar_width = self.get_app_prop2()[0]
            mid_op = setup_bar_width/4
            return (int(mid_op*pos), int(setup_bar_width/4))

        settings_type = {'suspension':1, 'dampers':2, 'gearing':3}
        self.app.set_focus()
        x, width = find_rst_settings(settings_type[settings])
        x, y, width, height = self.app_get_region(x, 70, width, 40, draw_outline=True)
        click_here(x+width/2, y+height/2, pause=.5, debug=True)

    def set_stats_gear_rst(self, gears):
        self.app.set_focus()
        self.app.set_focus()
        rst_pos_x, rst_pos_y = self.app.rectangle().left, self.app.rectangle().top
        rst_pos_height, rst_pos_width = self.app.rectangle().height(), self.app.rectangle().width()
        rst_width_mid = rst_pos_x+rst_pos_width/2
        rst_y_firstfield = rst_pos_y+180
        for gear, val in enumerate(gears):
            gui.click((rst_width_mid, rst_y_firstfield+55*gear))
            try:
                float(val)
                gui.typewrite(val)
            except ValueError:
                print(f'[ERROR] Gear {gear} ({val}) not a number')
                gui.typewrite('0')

    def set_stats_sus_rst(self, stats):
        self.app.set_focus()
        
        prop= self.get_app_prop2()
        seperator = prop[0]/3
        start = seperator/2

        pos = self.app_get_region(x=start, y=230)
        gui.click(pos[0], pos[1])
        gui.typewrite(stats[0])

        pos = self.app_get_region(x=start+seperator, y=230)
        gui.click(pos[0], pos[1])
        gui.typewrite(stats[2])

        pos = self.app_get_region(x=start, y=435)
        gui.click(pos[0], pos[1])
        gui.typewrite(stats[1])

        pos = self.app_get_region(x=start+seperator, y=435)
        gui.click(pos[0], pos[1])
        gui.typewrite(stats[3])

    def set_stats_damp_rst(self,stats):
        self.app.set_focus()
        
        prop= self.get_app_prop2()
        x_seperator_width = int(prop[0]/3)
        x_start = int(x_seperator_width/2)

        y_seperator_width = 50
        y_start_front = 230
        y_start_rear = 485

        front_damp = stats[0]
        rear_damp = stats[1]

        if len(front_damp) < 4:
            front_damp.extend(['1']*(4-len(front_damp)))

        if len(rear_damp) < 4:
            rear_damp.extend(['1']*(4-len(rear_damp)))

        for pos, stat in enumerate(front_damp):
            gui_pos = self.app_get_region(x=x_start, y=pos*y_seperator_width+y_start_front)
            gui.click(gui_pos[0], gui_pos[1])
            gui.typewrite(stat)

        for pos, stat in enumerate(rear_damp):
            gui_pos = self.app_get_region(x=x_start, y=pos*y_seperator_width+y_start_rear)
            gui.click(gui_pos[0], gui_pos[1])
            gui.typewrite(stat)