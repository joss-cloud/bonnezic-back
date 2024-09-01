import os

mp3_file = "/home/zic/JazzWorld/Gael Horellou - Children Of The Night.mp3"
print(f"Checking path: {mp3_file}")
print(f"File exists: {os.path.isfile(mp3_file)}")
print(f"Absolute path: {os.path.abspath(mp3_file)}")
print(f"Directory exists: {os.path.isdir(os.path.dirname(mp3_file))}")
