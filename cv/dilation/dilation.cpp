#include <iostream>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>

using std::cout;
using std::cerr;
using std::endl;

#define WINDOW_NAME "CV"
#define DEFAULT_LOWER_THRES .5
#define DEFAULT_UPPER_THRES_OFFSET .15

using namespace cv;

cv::Mat binarize(cv::Mat& img, double thres) {
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
	return thresh_img;
}

cv::Mat subtract(cv::Mat& lim, cv::Mat& uim) {
	Mat re = lim.clone();
	register int i, j;
	register Vec3b* rcol = re.ptr<Vec3b>(i = 0);
	register Vec3b* ucol = uim.ptr<Vec3b>(i);
	register Vec3b* lcol = lim.ptr<Vec3b>(i);

	size_t pixel_size = 3 * (size_t)(&(rcol[0][1]) - &(rcol[0][0]));

	do {
		for(j=0;j<re.cols;++j) {
			memset(&(rcol[j][0]), (lcol[j][0] == ucol[j][0]) ? 0xfff : 0x0, pixel_size);
		}
	} while(++i<re.rows && 0 != (
		(rcol = re.ptr<Vec3b>(i)) &&
		(lcol = lim.ptr<Vec3b>(i)) &&
		(ucol = uim.ptr<Vec3b>(i))
	));
	return re;
}

int main(int argc, char** argv) {

	if(argc < 2) {
		cerr << "No filename given" << endl;
		cout << "Usage: dilation <filename> [lower threshold] [upper threshold]";
		return 1;
	}

	char out[1000];
	sprintf(out, "%s-out.png", argv[1]);

	double lower_thres = DEFAULT_LOWER_THRES;
	double upper_thres;
	if(argc < 3) {
		cerr << "Defaulting threshold to " << DEFAULT_LOWER_THRES << endl;
		upper_thres = lower_thres + DEFAULT_UPPER_THRES_OFFSET;
	} else {
		lower_thres = ::atof(argv[2]);
		if(argc > 3) {
			upper_thres = ::atof(argv[3]);
		} else {
			upper_thres = lower_thres + DEFAULT_UPPER_THRES_OFFSET;
		}
	}

	Mat img = imread(argv[1], CV_LOAD_IMAGE_COLOR);
	if(!img.data) {
		cerr << "Could not open or find image" << endl;
		return 2;
	}

	cv::Mat lim = binarize(img, lower_thres);
	cv::Mat uim = binarize(img, upper_thres);
	cv::Mat sub = subtract(lim, uim);

	imwrite(out, sub);

	cout << "Done" << endl;

	// namedWindow(WINDOW_NAME, WINDOW_AUTOSIZE);
	// imshow(WINDOW_NAME, sub);

	// waitKey(0);

	return 0;
}
