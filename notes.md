### 硬件概述

摘选自wiki:

> FC使用一颗理光制造的8位2A03 NMOS处理器（基于6502中央处理器，但是缺乏BCD模式），PAL制式机型运行频率为1.773447MHz，NTSC制式机型运行频率为1.7897725MHz，主内存和显示内存为2KB。
> FC使用理光开发的图像控制器（PPU），有 2KB 的视频内存，调色盘可显示 48 色及 5 个灰阶。一个画面可显示 64 个角色(sprites) ，角色格式为 8x8 或 8x16 个像素，一条扫描线最多显示 8 个角色，虽然可以超过此限制，但是会造成角色闪烁。背景仅能显示一个卷轴，画面分辨率为 256x240 ，但因为 NTSC 系统的限制，不能显示顶部及底部的 8 条扫描线，所以分辨率剩下 256x224。
> 从体系结构上来说，FC有一个伪声音处理器 （pseudo-Audiom Processing Unit，pAPU），在实际硬件中，这个处理器是集成在2A03 NMOS处理器中的。pAPU内置了2个几乎一样（nearly-identical）的矩形波通道、1个三角波通道、1个噪声通道和1个音频采样回放通道（DCM，增量调制方式。其中3个模拟声道用于演奏乐音，1个杂音声道表现特殊声效（爆炸声、枪炮声等），音频采样回放通道则可以用来表现连续的背景音。

全部资料来源是[nesdev.com](http://nesdev.com/)



### 名词解释

本篇可能能遇到下列名词:

- CPU: 中央处理器, 即2A03
- PPU: 图形处理器, 用来控制/显示图形之类的
- VRAM: 即Video-RAM, 俗称显存
- PRG-ROM: 程序只读储存器: 存储程序代码的存储器. 放入CPU地址空间.
- CHR-ROM: 角色只读储存器, 基本是用来显示图像, 放入PPU地址空间
- VROM: 基本和CHR-ROM同义, 用于理解CHR-ROM
- SRAM: 存档(SAVE)用RAM, 有些卡带额外带了用电池供电的RAM
- WRAM: 工作(WORK)用RAM, 基本和SRAM一样, 不过不是用来存档, 就是拿来一般用的
- Mapper: 由于地址空间最多64KB, 当游戏太大时, 会使用Mapper/MMC用来切换当前使用的'BANK'. 软件(模拟器)上的实现, Mapper会把类似的MMC放在一起实现
- MMC: Memory-Management Controller 硬件(卡带)上的实现, 会有非常多的大类, 甚至还有变种. 在国内为了显示汉字还有魔改版
- CHR-RAM: 基本同CHR-ROM, 只不过可以写
- PRG-RAM: 基本同PRG-ROM, 只不过可以写



### FC游戏ROM

说到ROM, 目前流行的ROM格式是.nes格式的, 我参考的是叫做[NES 2.0](http://wiki.nesdev.com/w/index.php/NES_2.0)的ROM格式:

```
文件头:
 0-3: string    "NES"<EOF>
   4: byte      以16384(0x4000)字节作为单位的PRG-ROM大小数量
   5: byte      以 8192(0x2000)字节作为单位的CHR-ROM大小数量
   6: bitfield  Flags 6
   7: bitfield  Flags 7
8-15: byte      保留用, 应该为0. 其实有些在用了, 目前不管

CHR-ROM - 角色只读存储器(用于图像显示, 暂且不谈)

Flags 6:
7       0
---------
NNNN FTBM

N: Mapper编号低4位
F: 4屏标志位. (如果该位被设置, 则忽略M标志)
T: Trainer标志位.  1表示 $7000-$71FF加载 Trainer
B: SRAM标志位 $6000-$7FFF拥有电池供电的SRAM.
M: 镜像标志位.  0 = 水平, 1 = 垂直.

Byte 7 (Flags 7):
7       0
---------
NNNN xxPV

N: Mapper编号高4位
P: Playchoice 10标志位. 被设置则表示为PC-10游戏
V: Vs. Unisystem标志位. 被设置则表示为Vs.  游戏
x: 未使用
```



F: 由于FC的显存只有2kb, 只能支持2屏幕. 如果卡带自带了额外的显存就可以利用4屏幕了.

M: 同上, 这个标记为也暗示游戏是横版还是纵版.

可以看出很多其实不用忙着特地支持, 但是Trainer实现又很简单但是不急着实现的为了避免忘记 —— 打上TODO标记甚至FIXME是一个不错的选择.

### ROM在哪里

这里提供一个测试用的ROM, 这个ROM可以从一开始用到很后面:

- 原地址: [nestest](http://nickmass.com/images/nestest.nes)
- [以及文档](http://www.qmtpro.com/~nes/misc/nestest.txt)
- 收录地址: [Emulator tests](http://wiki.nesdev.com/w/index.php/Emulator_tests)



6502汇编使用数字前面美元符号($)作为16进制的表示(8086则是在后面加‘h’)

### CPU地址空间布局

先谈谈内存布局, 6502理论支持64KB的寻址空间, 但是小霸王服务器只有2kb的内存. 自然得说说内存布局

| 地址  | 大小  | 标记 | 描述          |
| ----- | ----- | ---- | ------------- |
| $0000 | $800  |      | RAM           |
| $0800 | $800  | M    | RAM           |
| $1000 | $800  | M    | RAM           |
| $1800 | $800  | M    | RAM           |
| $2000 | 8     |      | Registers     |
| $2008 | $1FF8 | R    | Registers     |
| $4000 | $20   |      | Registers     |
| $4020 | $1FDF |      | Expansion ROM |
| $6000 | $2000 |      | SRAM          |
| $8000 | $4000 |      | PRG-ROM       |
| $C000 | $4000 |      | PRG-ROM       |

M: 主内存2KB镜像, 比如读取$0800实际是读取$0000

R: PPU寄存器, 8字节步进镜像.

Registers: 一堆寄存器, 现在不用管.

Expansion ROM: 扩展ROM, 现在不用管

SRAM, PRG-ROM: 已经说过了

### 

6502有三种中断(按优先度排序, 越后面越优先):

- IRQ/BRK
- NMI
- RESET

每一种中断都有一个向量. 向量是当中断触发时“转到”的指定位置的16位地址:

- $FFFA-FFFB = NMI
- $FFFC-FFFD = RESET
- $FFFE-FFFF = IRQ/BRK

1. IRQ - Interrupt Request 中断请求 硬件中断请求被执(大致分为Mapper和APU两类)
2. BRK - Break 中断指令 当软件中断请求被执行(BRK指令)
3. NMI - Non-Maskable Interrupt 不可屏蔽中断 发生在每次垂直空白(VBlank)时, NMI在NTSC制式下刷新次数为 60次/秒, PAL为50次/秒
4. RESET在(重新)启动时被触发. ROM被读入内存, 6502跳转至指定的RESET向量

也就是说程序一开始执行`$FFFC-FFFD`指向的地址

'低地址'在'低地址', '高地址'在'高地址'. 即低8位在$FFFC, 高8位在$FFFD.

### Mapper000 - NROM

目前当然是实现Mapper000, 实际上也就是没有Mapper的意思:

- 适用于16KB(NROM-128)或者32KB(NROM-256)的PRG-ROM
- CPU `$8000-$BFFF`: ROM开始的16kb
- CPU `$C000-$FFFF`: ROM最后的16kb

### 