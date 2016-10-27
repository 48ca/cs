#include <iostream>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>

using std::cout;
using std::cerr;
using std::endl;

#define WINDOW_NAME "CV"
#define DEFAULT_THRES .5

using namespace cv;

int main(int argc, char** argv) {

	if(argc < 2) {
		cerr << "No filename given" << endl;
		return 1;
	}

	double thres = DEFAULT_THRES;
	if(argc < 3) {
		cerr << "Defaulting threshold to " << DEFAULT_THRES << endl;
	} else {
		thres = ::atof(argv[2]);
	}

	Mat img = imread(argv[1], CV_LOAD_IMAGE_COLOR);
	if(!img.data) {
		cerr << "Could not open or find image" << endl;
		return 2;
	}

	Mat thresh_img = img.clone();
	uchar thresh = (uchar)(thres * 0xfff * 3);
	register int i, j;
	register Vec3b* col = thresh_img.ptr<Vec3b>(i = 0);
	size_t pixel_size = 3 * (size_t)(&(col[0][1]) - &(col[0][0]));

	do {
		for(j=0;j<thresh_img.cols;++j) {
			memset(&(col[j][0]), (col[j][0] + col[j][1] + col[j][2]) > thresh ? 0xfff : 0x0, pixel_size);
		}
	} while(++i<thresh_img.rows && NULL != (col = thresh_img.ptr<Vec3b>(i)));

	imwrite("out.png", thresh_img);
	return 0;

	namedWindow(WINDOW_NAME, WINDOW_AUTOSIZE);
	imshow(WINDOW_NAME, thresh_img);

	waitKey(0);

	// binarize -- come up with a threshold
	// segmentation

	return 0;
}
