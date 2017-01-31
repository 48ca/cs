#include <stdio.h>
#include <opencv2/opencv.hpp>
#include <vector>
// #include "platonic.hpp"

using namespace cv;
using std::vector;

int main(int argc, char** argv )
{
	if ( argc != 2 )
	{
		printf("usage: a.out <path>\n");
		return 1;
	}

	VideoCapture cap(argv[1]);

	if ( !cap.isOpened() )
	{
		printf("No video data \n");
		return 2;
	}

	namedWindow("Display Video", WINDOW_AUTOSIZE);

	Mat frame0;
	Mat frame1;
	vector<KeyPoint> keypoints_frame0;
	vector<KeyPoint> keypoints_frame1;
	Mat descriptors_frame0;
	Mat descriptors_frame1;

	vector< vector<DMatch> > matches01;
	vector< vector<DMatch> > matches10;
	Ptr<DescriptorMatcher> matcher = BFMatcher::create();

	vector<DMatch> good_matches0;
	vector<DMatch> good_matches1;

	Ptr<FeatureDetector> detector = ORB::create();
	Ptr<DescriptorExtractor> extractor = ORB::create();
	while(true)
	{
		cap >> frame1;
		detector->detect(frame1, keypoints_frame1);
		if(frame0.empty()) {
			frame0 = frame1;
			keypoints_frame0 = keypoints_frame1;
			continue;
		}

		extractor->compute(frame0,keypoints_frame0,descriptors_frame0);
		extractor->compute(frame1,keypoints_frame1,descriptors_frame1);

		matcher->knnMatch(descriptors_frame0, descriptors_frame1, matches01, 2);
		matcher->knnMatch(descriptors_frame1, descriptors_frame0, matches10, 2);

		double max_dist = 0;
		double min_dist = 100;
		int i;
		for(i=0;i<descriptors_frame0.rows;++i) {
			double dist = matches01[i].data()->distance;
			if(dist < min_dist)
				min_dist = dist;
			if(dist > max_dist)
				max_dist = dist;
		}

		double ratio = .9;

		// http://stackoverflow.com/questions/35194681/how-to-compare-two-group-keypoint-in-opencv
		for(i=0;i<matches01.size();++i)
			if(matches01[i][0].distance < ratio * matches01[i][1].distance)
				good_matches0.push_back(matches01[i][0]);
		for(i=0;i<matches10.size();++i)
			if(matches10[i][0].distance < ratio * matches10[i][1].distance)
				good_matches1.push_back(matches10[i][0]);

		vector<DMatch> symmetric_matches;
		
		/*
		for(KeyPoint kp : keypoints_frame0) {
			Point2f pt = kp.pt;
		}
		*/

		Mat output = frame0.clone();
		// drawShape(output);
		// drawMatches(frame0, keypoints_frame0, frame1, keypoints_frame1, matches01, output);
		
		imshow("Display Video", output);
		waitKey(30);
	}

	return 0;
}
