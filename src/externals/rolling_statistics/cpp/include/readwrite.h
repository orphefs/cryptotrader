#pragma once

#include <vector>
#include <string>
#include <fstream>

void computeRollingStats(std::string const t_readfilePath, std::string const t_writeFilePath);
std::ifstream openStream(std::string const t_filePath);