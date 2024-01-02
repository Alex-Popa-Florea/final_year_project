Here is some information of the files in this folder:

1. This folder mainly uses the speech service of Azure, a comprehensive cloud computing platform and infrastructure service offered by Microsoft. Our main purpose is to use the `Real time diarization` service, however, it is currently under public review. So we are using the `Speaker diarization` service instead, this will generate a similar output while we need to get the voice information beforehand.

2. `main.cpp` contains the code for speaker recognition and can be successfully compiled at the moment. Before running the code, remember to register with the Microsoft Azure and create a speech resource to get your own subscription keys. Note that there are still some bugs need to be fixed.

3. The voice information will be collected throught the self-introduction part of the participants. Ideally, a 2-minutes self-intro would be enough.

4. For those who farmiliar with cpp, I would recomand that you try with the real time diarisation service first. Although it is now under puclic review, it is currently the most suitable service for our project based on our opinion.

5. I would recommand to use Azure on a linux system as it is much esier to do so than on Macos. If the speechSDK still does not support the mentioned 2 services in Python and you are not farmiliar with any other language besides Python like me, I would recommand you not using cpp.

6. More detailes will be included in the Tutorial.