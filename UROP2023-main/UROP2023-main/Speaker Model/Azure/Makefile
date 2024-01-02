# Makefile template

# Compiler and compiler flags
CC := g++
INCLUDE := -Iinclude/cxx_api/ -Iinclude/c_api
CFLAGS := -g -std=c++20 $(INCLUDE)
LIBDIR := -L 'lib/x64' '/lib/x86_64-linux-gnu/libstdc++.so.6'
LIBS := -lMicrosoft.CognitiveServices.Speech.core \
				-lMicrosoft.CognitiveServices.Speech.extension.kws \
				-lMicrosoft.CognitiveServices.Speech.extension.audio.sys \
				-lMicrosoft.CognitiveServices.Speech.extension.lu \
				-lMicrosoft.CognitiveServices.Speech.extension.codec \
				-lMicrosoft.CognitiveServices.Speech.extension.mas \
				-lMicrosoft.CognitiveServices.Speech.extension.kws.ort 


main.o: main.cpp
	$(CC) $(CFLAGS) $(HEADERS) -c $^

main: main.o
	$(CC) $(CLAGS) -o $@ $(LIBDIR) $^ $(LIBS)

clean:
	rm -f *.o main

