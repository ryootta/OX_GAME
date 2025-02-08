import pyxel

SCREEN_WIDTH = 90 
SCREEN_HEIGHT = 120
START_SCENE = "start"
PLAY_SCENE = "play"
GAME_OVER_DISPLAY_TIME = 60
CELL_SIZE = 30

class O:
    def __init__(self, x, y):
        size = 16
        x_center = SCREEN_WIDTH // 2
        #self.x = x_center - (CELL_SIZE * (1 - x)) - (size // 2)
        self.x = SCREEN_WIDTH * (x) // 3 + size // 2 
        print(self.x)
        self.y = SCREEN_HEIGHT * (1 + y) // 4
    
    def draw(self):
        pyxel.blt(self.x , self.y, 0, 0, 0, 16, 16, pyxel.COLOR_BLACK)

class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="OX GAME")
        pyxel.mouse(True)
        pyxel.load("my_resource.pyxres")
        self.current_scene = START_SCENE
        self.is_game_over = False
        self.os = []
        self.game_over_display_timer = GAME_OVER_DISPLAY_TIME
        pyxel.run(self.update, self.draw)


    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        if self.current_scene == START_SCENE:
            self.update_start_scene()
        elif self.current_scene == PLAY_SCENE:
            self.update_play_scene()

    def draw(self):
        if self.current_scene == START_SCENE:
            self.draw_start_scene()
        elif self.current_scene == PLAY_SCENE:
            self.draw_play_scene()

    def reset_play_scene(self):
        self.is_game_over = False
        self.game_over_display_timer = GAME_OVER_DISPLAY_TIME
    
    def update_start_scene(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.reset_play_scene()
            self.current_scene = PLAY_SCENE  
    
    def update_play_scene(self):
        if self.is_game_over:
            if self.game_over_display_timer > 0:
                self.game_over_display_timer -= 1
            else:
                self.current_scene = START_SCENE
            return

        x = -1
        y = -1
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if 0 <= pyxel.mouse_x < SCREEN_WIDTH * 1 // 3:
                x = 0
            elif SCREEN_WIDTH // 3 <= pyxel.mouse_x < SCREEN_WIDTH * 2 // 3:
                x = 1 
            elif SCREEN_WIDTH * 2 // 3 <= pyxel.mouse_x < SCREEN_WIDTH: 
                x = 2

            if SCREEN_HEIGHT // 4 <= pyxel.mouse_y < SCREEN_HEIGHT * 2 // 4:
                y = 0
            elif SCREEN_HEIGHT * 2 // 4 <= pyxel.mouse_y < SCREEN_HEIGHT * 3 // 4:
                y = 1
            elif SCREEN_HEIGHT * 3 // 4 <= pyxel.mouse_y < SCREEN_HEIGHT:
                y = 2
                 
        #    self.is_game_over = True

        if not (x == -1) or not (y == -1):
            self.os.append(O(x, y))

    def draw_start_scene(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        pyxel.text(70, 60, "Click to Start !", pyxel.COLOR_YELLOW)
        
    def draw_play_scene(self):
        pyxel.cls(pyxel.COLOR_CYAN)
        pyxel.text(0, 0, "play", pyxel.COLOR_YELLOW)

        for o in self.os:
            o.draw()

        if self.is_game_over:
            pyxel.text(SCREEN_WIDTH // 2 - 20, SCREEN_WIDTH // 2, 
                        "Game Over" , pyxel.COLOR_YELLOW)




App()