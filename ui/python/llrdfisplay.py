#!/usr/bin/python3

from epics import caget, caput, cainfo, ca, PV
import pygame, sys
import pygame.freetype
import random

import multiprocessing as mp
import signal
import time

run = mp.Value('b', True)

COLOR_SET = [pygame.Color('#66bb00'), pygame.Color('#84b200'), pygame.Color('#9ea800'), pygame.Color('#b69c00'), 
             pygame.Color('#cc8f00'), pygame.Color('#df7f00'), pygame.Color('#f06c00'), pygame.Color('#ff5600')]
#66bb00
#84b200
#9ea800
#b69c00
#cc8f00
#df7f00
#f06c00
#ff5600

def sstop(signal, frame):
    global run
    run.value = False

signal.signal(signal.SIGINT, sstop)
signal.signal(signal.SIGTERM, sstop)

def display(run, v):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    
    pygame.init()
    pygame.font.init()

    flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
    screen = pygame.display.set_mode((480,800), flags)
#    screen = pygame.display.set_mode((480,800))
    print(screen) # check if HW rendering works
    pygame.display.set_caption("RFBOX")
    pygame.mouse.set_visible(0) # hide cursor

    clock = pygame.time.Clock()

    FONT = pygame.freetype.SysFont("Arial", 20)
    FONT_OLDSYSTEM = pygame.font.SysFont("Arial", 20) # second instance with old font system because new cant align right
    SMALL_FONT = pygame.freetype.SysFont("Arial", 12)
    SMALL_FONT_OLDSYSTEM = pygame.font.SysFont("Arial", 12) # again old font system

    def update_fps():
        fps = str(int(clock.get_fps()))
        fps_text = SMALL_FONT_OLDSYSTEM.render(fps, 1, pygame.Color("coral"))
        return fps_text

    # init bar variables with sane firsts
    font_height = 60
    val_min = -30
    val_max = 10
    full_width = abs(val_min) + abs(val_max)
    val_quarter = full_width / 4
    step_size = (screen.get_size()[0] / 4 * 2) / full_width
    x_start = (screen.get_size()[0] / 4 * 1)

    # draw RFBOX Headline
    nullsurface = pygame.Surface((480,800)) # otherwise it would display the title twice
    headline = FONT.render_to(nullsurface, (0,0),"RFBOX", WHITE)
    headline.center = (screen.get_size()[0] / 2, 30)

    # make a rect for the bars
    pv_bar_border = pygame.Rect(x_start, font_height, full_width * step_size + 1, 20)

    while run.value:
        clock.tick(30)
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                # If pressed key is ESC quit program
                if event.key == pygame.K_ESCAPE:
                    run.value = False
            if event.type == pygame.QUIT:
                run.value = False
        
        screen.fill(BLACK)
        screen.blit(update_fps(), (10,0))
        screen.blit(nullsurface, headline)

        # render bars for each available PV
        cnt = 0
        for pvname, pv in v.items():
            if any(x in pvname for x in ["_inverse", "_egu", "_lopr", "_hopr"]):
                continue

            if "___" == pvname:
                # divider line
                font_height += 20
                pygame.draw.rect(screen, pygame.Color("#871607"), (0, font_height, screen.get_size()[0], 5))
                font_height += 15
                font_height += 20
                cnt = 0
                continue
            
            try:
                if pvname + "_inverse" in v.keys():
                    val_min = v[pvname + "_hopr"]
                    val_max = v[pvname + "_lopr"]
                    inverse = True
                else:
                    val_min = v[pvname + "_lopr"]
                    val_max = v[pvname + "_hopr"]
                    inverse = False
                full_width = abs(val_min) + abs(val_max)
                val_quarter = full_width / 4
                step_size = (screen.get_size()[0] / 4 * 2) / full_width
            except KeyError:
                pass

            if pv is not None:
                x_length = step_size * (pv - val_min) # bar length
                if inverse:
                    x_length = -x_length # reverse direction
            else:
                x_length = 1
            
            SMALL_FONT.render_to(screen, (10, font_height + 6), pvname[-14:], WHITE)
            #pygame.draw.rect(screen, r,g,b), (x, y, width, height))
            bar_color = COLOR_SET[cnt]
            pv_bar_border.top = font_height # move border box down
            pygame.draw.rect(screen, bar_color, (x_start, font_height, x_length, 20)) # the actual value bar
            try:
                text_value = FONT_OLDSYSTEM.render(" {:+5.2f} ".format(pv) + v[pvname + "_egu"], True, WHITE)
            except TypeError:
                text_value = FONT_OLDSYSTEM.render("  NaN", True, WHITE)
            text_rect = text_value.get_rect()
            text_rect.top = font_height - 2
            text_rect.right = screen.get_size()[0] - 5
            screen.blit(text_value, text_rect)

            # write LOPR and HOPR in quarters
            try:
                SMALL_FONT.render_to(screen, (x_start + (val_quarter * 0 * step_size) + 5, font_height + 22), str(val_min), WHITE)
                SMALL_FONT.render_to(screen, (x_start + (val_quarter * 1 * step_size) + 5, font_height + 22), str(val_min + val_quarter), WHITE)
                SMALL_FONT.render_to(screen, (x_start + (val_quarter * 2 * step_size) + 5, font_height + 22), str(val_min + 2*val_quarter), WHITE)
                SMALL_FONT.render_to(screen, (x_start + (val_quarter * 3 * step_size) + 5, font_height + 22), str(val_max - val_quarter), WHITE)
                SMALL_FONT.render_to(screen, (x_start + (val_quarter * 4 * step_size) + 5, font_height + 22), str(val_max), WHITE)
            except TypeError:
                pass

            font_height += 40 # add offset so that the bars dont stack
            if cnt == len(COLOR_SET) - 1:
                cnt = 0
            else:
                cnt += 1
        font_height = 60

        pygame.display.flip()

    pygame.quit()
    print("stopped pygame window")

def getter(run, v, v_lock, pvname):
    pv = PV(pvname)
    while run.value:
        val = pv.get(timeout=0.2)
        if val is not None:
            with v_lock:
                v[pvname] = val
                v[pvname + "_egu"] = pv.units
                v[pvname + "_lopr"] = pv.lower_ctrl_limit
                v[pvname + "_hopr"] = pv.upper_ctrl_limit
        time.sleep(0.1)
    print("stopping getter for " + pvname)

if __name__ == '__main__':
    with mp.Manager() as manager:
        v = manager.dict()
        v_lock = mp.Lock()
        # HAT0
        v["MCC:LLRFSRC:GUN"] = None
        v["MCC:LLRFSRC:BUNCHER"] = None
        v["MCC:LLRFSRC:K1"] = None
        v["MCC:LLRFSRC:K2"] = None
        v["MCC:LLRFSRC:KICKER"] = None
        v["MCC:LLRFSRC:PSU_TEMP"] = None
        v["___"] = None # divider line

        loopgetters = []
        for pv in v:
            if pv == "___" or "_inverse" in pv:
                continue

            print("pv: " + pv)
            loopgetter = mp.Process(target=getter, args=(run, v, v_lock, pv, ))
            loopgetters.append(loopgetter)
            loopgetter.start()
        
#        loopdisplay = mp.Process(target=display, args=(run, v, ))
#        loopdisplay.start()

        print("started procs")
        display(run, v) # directly run the display function in the main thread
#        while run.value:
#            time.sleep(1)

        for proc in loopgetters:
            proc.join()

#        loopdisplay.join()

        
    print("end")
