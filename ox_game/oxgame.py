import pyxel

class App:
    def __init__(self):
        pyxel.init(160, 120, title="OX GAME")
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

    def draw(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        pyxel.text(70, 60, "Start", pyxel.COLOR_YELLOW)

App()