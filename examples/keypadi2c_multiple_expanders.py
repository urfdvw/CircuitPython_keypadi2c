# python native
from time import monotonic

#%% imports
import gc
# Cpy native
import board
import busio
# Adafruit
from adafruit_mcp230xx.mcp23017 import MCP23017
# My
from keypadi2c import I2CKeyPad, I2CKeys

#%% keypad defination
# I2C
SCL = board.SCL
SDA = board.SDA
i2c = busio.I2C(SCL, SDA, frequency=int(1e6))
keypad = I2CKeyPad([
    I2CKeys(mcp=MCP23017(i2c, 0x20), nbits=16, code_shift=0),
    I2CKeys(mcp=MCP23017(i2c, 0x21), nbits=16, code_shift=16),
    I2CKeys(mcp=MCP23017(i2c, 0x22), nbits=16, code_shift=32),
    I2CKeys(mcp=MCP23017(i2c, 0x23), nbits=16, code_shift=48),
])

#%% main
while True:
    event = keypad.events.get()
    if event:
        print(event)
        gc.collect()