Here's an introduction to files in this folder:

1. `misty_utterance` contains some basic knowledge about using misty robot locally via python. I have to say that currently I am not able to run the code locally but can only play aroung with the robot using the MistyStudio website. More information about the misty website will be included in the Tutorial.

2. For the folder `Skills_and_Tasks`, It contains two files: `skills` and `tasks`. I will explain these two files separately.

3. Based on the code from our mentor Nicole, in order to better assess the user's learning situation, we first listed some skills required to complete the tasks we want to test. These skills and tasks are listed inside the file `skills.ipynb`. We have 21 skills in total. You are encouraged to add more skills if you want to add some more tasks.

4. File `tasks.py` defines classes for skills and tasks related to our project. We will create a vector of the skills like the following:
```python
all_skills = [sk_led, sk_FM,sk_buzzer,sk_switch, sk_reed, sk_button,sk_lamp, sk_battery, sk_speaker, sk_music, sk_motor,sk_cp, sk_dir_led, power_mc, signal_mc, power_fm, signal_fm, closed_circuit,and_gate,or_gate,not_gate]
```
which represents:
```python
all_skills = [skill_1, skill_2, skill_3, ..., skill_21]
```
We will use this to represent the skills that will be used in each task in the following setting:
```python
task1 = Task(1,"sw_la", ["switch", "lamp"], [], 
		[0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],
		"Build a circuit that you can turn a light on and off using a switch")
```
The above code is for task 1: Build a circuit that you can turn a light on and off using a switch. As you can see from the vector in the above code, 0 represents that this skill will not be used during this task while 1 represents that this skill will be tested. `sw_la` will be the name of the task and the following list indicates the electronic components that will be used during this task.