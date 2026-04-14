import time
import numpy as np
def SoftSetJointCompliance(robot, target_k, tm):
    # Get the current joint stiffness values
    k0 = robot.joint_compliance.K
    
    # Calculate the number of steps
    N = max(1, round(tm / robot.tsamp))
    
    # Calculate the incremental changes 
    dK = (target_k - k0) / N
    dK = dK.astype(np.int64)

    #initialize
    Ki = k0
    target_d = robot._franka_default.JointCompliance.D

    robot.controller._verbose = 0
    # Gradually update compliance
    for i in range(1, N):
        Ki += dK
        robot.SetJointCompliance(Ki,target_d)
        time.sleep(robot.tsamp)
        
    robot.controller._verbose = 1
    robot.SetJointCompliance(Ki+dK,target_d)


import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"  # Suppress the welcome message
import pygame

def pip(freq=440, dur=0.5, rep=1):
    """
    Generate a sound with the given frequency, duration, and repetitions.

    Parameters:
    freq (int): Frequency of the sound in Hz (default 440 Hz).
    dur (float): Duration of the sound in seconds (default 0.5 seconds).
    rep (int): Number of repetitions (default 1).
    """
    fs = 8196  # Sample frequency
    
    # Generate the sound wave
    t = np.arange(0, dur, 1/fs)  # Time vector
    sound_wave = np.sin(2 * np.pi * freq * t) * 32767  # Scale to int16

    # Initialize pygame mixer
    pygame.mixer.init(frequency=fs, size=-16, channels=1)

    # Convert numpy array to sound format
    sound_array = np.array(sound_wave, dtype=np.int16)
    sound = pygame.sndarray.make_sound(sound_array)

    # Play the sound for the specified repetitions
    for _ in range(rep):
        sound.play()
        time.sleep(dur + 0.1)  # Pause between repetitions