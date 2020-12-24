# import board
# import digitalio
# import storage
 
# switch = digitalio.DigitalInOut(board.D12)
# switch.direction = digitalio.Direction.INPUT
# switch.pull = digitalio.Pull.UP
 
# # If the D12 is connected to ground with a wire
# # CircuitPython can write to the drive
# storage.remount("/", switch.value)


## Going into read-mode

# For when you want to register the data.

# 1. Set the following as your `boot.py`.

# ```python
#     import storage

#     storage.remount("/", False)
# ```

# 2. Press the `reset` button on the micro-controller. That's it.

## Going into write-mode

# For when you want to edit the code.

# 1. Open the REPL (I used the Mu code editor)
# 2. Run the following:

# ```
#     >>> import os
#     >>> os.listdir("/")
#     >>> os.rename("/boot.py", "/boot.bak")
# ```
# 3. Press the `reset` button on the micro-controller.


import storage
 
storage.remount("/", False)