# -*- coding: utf-8 -*-
import pygame as pg

import nes_cpu as nc
import nes_file as nf
import utils


def main():
    width, height = 256, 240
    screen = pg.display.set_mode((width, height))
    clock = pg.time.Clock()
    running = True
    fps = 30
    # scale = 10

    nes = nf.NesFile.load('misc/nestest.nes')
    cpu = nc.NesCPU()
    cpu.load_nes(nes)

    rl = cpu.mem_value(0xfffc)
    rh = cpu.mem_value(0xfffd)
    reset = utils.number_from_bytes([rl, rh])
    cpu.set_reg_value('pc', reset)
    for _ in range(20000):
        cpu.execute()

    while running:
        cpu.draw(screen)
        # for idx, code in enumerate(memory):
        #     x = idx % 10
        #     y = idx // 10
        #     color = parse_rgba(code)
        #     utils.log('x: <{}>\ny: <{}> \ncolor: <{}>'.format(x, y, color))
        #
        #     for w in range(scale):
        #         for h in range(scale):
        #             position = (x * scale + w, y * scale + h)
        #             screen.set_at(position, color)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        pg.display.flip()
        clock.tick(fps)


if __name__ == '__main__':
    main()
