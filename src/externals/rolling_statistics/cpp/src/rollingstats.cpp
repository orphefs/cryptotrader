#include "rollingstats.h"
#include <deque>
#include <iostream>

RollingMean::RollingMean(std::size_t windowSize_t) : m_windowSize(windowSize_t)
{
}

void RollingMean::insertSample(float const &sample_t)
{
    m_newSample = sample_t;
    selectMode();
    // std::cout << static_cast<std::underlying_type<Mode>::type>(m_mode) << std::endl;
    switch (m_mode)
    {
    case Mode::CUMULATIVE:
        m_samples.push_back(sample_t);
        break;
    case Mode::ROLLING:
        m_samples.push_back(sample_t);
        m_oldSample = m_samples[0];
        m_samples.pop_front();
        break;
    default:
        break;
    }
    updateState();
}

float RollingMean::computeMean(std::deque<float> const &m_samples)
{
    float mean(0.0);
    for (auto it = m_samples.begin(); it != m_samples.end(); ++it)
    {
        mean += *it * (1.0 / m_samples.size());
    }
    return mean;
}

void RollingMean::selectMode()
{
    if (m_samples.size() < m_windowSize)
    {
        m_mode = Mode::CUMULATIVE;
    }
    else
    {
        m_mode = Mode::ROLLING;
    }
}

void RollingMean::updateState()
{
    switch (m_mode)
    {
    case Mode::CUMULATIVE:
        m_newMean = RollingMean::computeMean(m_samples);
        break;
    case Mode::ROLLING:
        m_newMean = m_oldMean + (m_newSample / m_windowSize) - (m_oldSample / m_windowSize);
        break;
    default:
        break;
    }
    m_oldMean = m_newMean;
}