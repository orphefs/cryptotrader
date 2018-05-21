#include <vector>

class TimeSeries final
{
  public:
    TimeSeries(std::vector<float> const & timeSeries_t);
    std::vector<float> getTimeseries() const { return m_timeSeries; };
    float & operator[] (int i){return m_timeSeries[i];};
  private:
    std::vector<float> m_timeSeries;
};