# Introduction
This library is an extension to the CircuitPython `keypad` module.
It is used when MCP I2C IO expanders are used, and each expanded IO PIN is connected to a key switch.
Another way to describe the setting is that I2C IO expanders are used to replace shift registers, no matrix.

The library is designed to be compatible with the native keypad module,
in the way that you can read key events by `keypadi2c.events.get()`.
However, there are some differences
- It does not have the same speed performance as the native module, which is written in C++.
    - The scan speed is adequate for regular typing. 
        - In my test with RP2040 and 4 MCP23017 IO expanders, the scan frequency is above 400Hz
- The events are not strictly ordered according to keystrokes.
    - This is not visible at an ordinary human being's typing speed.
    - But might effect gameplay if keystrok order matters, such as rhythm games like DDR.

Please see examples for details.