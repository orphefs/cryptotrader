#include "timeseries.h"
#include "boost/algorithm/string.hpp"
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include "rollingstats.h"
#include <experimental/filesystem>
namespace fs = std::experimental::filesystem;

std::ifstream openStream(std::string const t_filePath)
{
    std::ifstream infile(t_filePath);
    if (!infile.is_open())
    {
        std::cout << "Failed to open file " + t_filePath + "\n";
    }
    else
    {
        std::cout << "Opened file" + t_filePath + "\n";
    }

    return infile;
}

void computeRollingStats(std::string const t_readfilePath, std::string const t_writeFilePath)
{
    std::ifstream infile = openStream(t_readfilePath);
    std::string line;
    std::vector<std::string> lineTokens;
    std::ofstream m_loggingStream;
    m_loggingStream.open(t_writeFilePath, std::ofstream::out | std::ofstream::trunc);
    RollingMean myRollingMean(std::size_t{1000});
    while (std::getline(infile, line))
    {
        boost::split(lineTokens, line, boost::is_any_of(","));
        myRollingMean.insertSample(std::stof(lineTokens[1]));
        m_loggingStream << lineTokens[0] << "," << myRollingMean.getRollingMean() << "\n";
    }
    infile.close();
    m_loggingStream.close();
}
