LDLIBS=`pkg-config opencv --cflags --libs`
CCFLAGS=-O3 -Wall -Wextra
CXX=g++

(all):
	$(CXX) $(CCFLAGS) dilation.cpp $(LDLIBS)
