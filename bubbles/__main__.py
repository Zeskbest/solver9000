from bubbles import Game, Bottle, yellow, orange, red, blue, lightgreen, pink, brown, purple, gray, green, \
    lightblue, sea

if __name__ == '__main__':
    game = Game(
        Bottle(sea, purple, sea, gray),
        Bottle(orange, pink, red, blue),
        Bottle(blue,lightblue,lightblue,pink),
        Bottle(purple,blue,red,gray),
        Bottle(orange,sea,orange,lightblue),
        Bottle(lightgreen,pink,purple,sea),

        Bottle(lightblue,lightgreen,gray,purple),
        Bottle(blue,orange,red,gray),
        Bottle(pink,lightgreen,red,lightgreen),
        Bottle(),
        Bottle(),
    )
    game.solve()
    game.show()
    input()
