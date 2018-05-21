#include <iostream>
#include "timeseries.h"
#include "rollingstats.h"
#include "readwrite.h"


int main()
{

    std::cout << "Hello World" << std::endl;
    std::vector<float> sampleData{1.0, 2.0, 3.0};
    TimeSeries myTimeSeries(sampleData);
    std::vector<float> sampleData1 = myTimeSeries.getTimeseries();


    computeRollingStats("data/test2/in.txt", "data/test2/out.txt");
    
    
    


    return 0;
}