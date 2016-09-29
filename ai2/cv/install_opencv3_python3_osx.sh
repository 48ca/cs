# brew install python3
# pip3 install numpy
# brew install cmake
git clone --depth=1 https://github.com/Itseez/opencv.git
cd opencv
mkdir build
cd build
# note: in the next line, adjust paths to point to the correct python version
cmake -DBUILD_opencv_python3=YES -DBUILD_opencv_python2=NO -DINSTALL_PYTHON_EXAMPLES=YES -DPYTHON3_EXECUTABLE=/usr/bin/python3 -DPYTHON3_INCLUDE_DIR=/usr/include/python3.4  -DPYTHON3_NUMPY_INCLUDE_DIRS=/usr/lib/python3.4/site-packages/numpy/core/include/ -DPYTHON3_PACKAGES_PATH=/usr/lib/python3.4/site-packages/ ..
make -j8
make install
python3 -c "import cv2; print(cv2.__version__)"
