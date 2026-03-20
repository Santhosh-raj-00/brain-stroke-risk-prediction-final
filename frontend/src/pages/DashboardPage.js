import React, { useState, useEffect } from 'react';
import { Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import styled from 'styled-components';
import axios from 'axios';

// Register chart components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend
);

const DashboardContainer = styled.div`
  min-height: 100vh;
  background-color: #EEF1F5;
  padding: 32px;
`;

const ContentWrapper = styled.div`
  max-width: 1440px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-column-gap: 24px;
  grid-row-gap: 32px;
`;

const Header = styled.div`
  grid-column: 1 / -1;
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
`;

const DashboardTitle = styled.h1`
  color: #1F2937;
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 12px;
  text-align: left;
`;

const Subtitle = styled.p`
  color: #6B7280;
  font-size: 16px;
  text-align: left;
`;

const StatsGrid = styled.div`
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-column-gap: 24px;
  margin-bottom: 0;
`;

const StatCard = styled.div`
  background: #F6F8FB;
  border-radius: 20px;
  padding: 24px;
  text-align: center;
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  box-shadow:
    8px 8px 18px #D1D9E6,
    -8px -8px 18px #FFFFFF;
`;

const StatValue = styled.div`
  font-size: 32px;
  font-weight: 700;
  color: #6C7CFF;
  margin-bottom: 8px;
`;

const StatLabel = styled.div`
  color: #6B7280;
  font-size: 14px;
`;

const ChartsGrid = styled.div`
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-column-gap: 24px;
  grid-row-gap: 32px;
  margin-bottom: 0;
`;

const ChartCard = styled.div`
  background: #F6F8FB;
  border-radius: 20px;
  padding: 24px;
  height: 360px;
  display: flex;
  flex-direction: column;
  box-shadow:
    8px 8px 18px #D1D9E6,
    -8px -8px 18px #FFFFFF;
  overflow: hidden;
`;

const ChartTitle = styled.h3`
  color: #1F2937;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  text-align: left;
`;

const AlertsContainer = styled.div`
  grid-column: 1 / -1;
  background: #F6F8FB;
  border-radius: 20px;
  padding: 24px;
  box-shadow:
    8px 8px 18px #D1D9E6,
    -8px -8px 18px #FFFFFF;
`;

const AlertsTitle = styled.h3`
  color: #1F2937;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  text-align: left;
`;

const AlertItem = styled.div`
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #E5E7EB;
  
  &:last-child {
    border-bottom: none;
  }
`;

const AlertText = styled.div`
  color: #1F2937;
  font-size: 14px;
`;

const AlertRisk = styled.div`
  color: ${props => {
    if (props.level === 'HIGH') return '#EF4444';
    if (props.level === 'MEDIUM') return '#F59E0B';
    return '#22C55E';
  }};
  font-size: 14px;
  font-weight: 500;
`;

const DashboardPage = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [demographicsData, setDemographicsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!localStorage.getItem('authToken')) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        // Base URL configuration
        const baseUrl = process.env.REACT_APP_API_URL && process.env.REACT_APP_API_URL !== '/'
          ? process.env.REACT_APP_API_URL
          : '';

        // API Endpoints
        const summaryUrl = `${baseUrl}/api/dashboard/summary`;
        const riskDistributionUrl = `${baseUrl}/api/dashboard/risk-distribution`;
        const patientsUrl = `${baseUrl}/api/dashboard/patients`;
        const shapUrl = `${baseUrl}/api/dashboard/shap`;

        const authHeader = {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
          }
        };

        // Fetch all data in parallel
        const [summaryResponse, riskResponse, demographicsResponse, shapResponse] = await Promise.all([
          axios.get(summaryUrl, authHeader).catch(err => ({ error: err })),
          axios.get(riskDistributionUrl, authHeader).catch(err => ({ error: err })),
          axios.get(patientsUrl, authHeader).catch(err => ({ error: err })),
          axios.get(shapUrl, authHeader).catch(err => ({ error: err }))
        ]);

        // Handle successful responses
        const summaryData = !summaryResponse.error ? summaryResponse.data : null;
        const riskData = !riskResponse.error ? riskResponse.data : null;
        const demographicsData = !demographicsResponse.error ? demographicsResponse.data : null;
        const shapData = !shapResponse.error ? shapResponse.data : [];

        if (!summaryData && !riskData && !demographicsData) {
          throw new Error('Failed to fetch dashboard data');
        }

        // Process SHAP data
        let transformedShapData = [];
        if (shapData && Array.isArray(shapData)) {
          transformedShapData = shapData.map(item => ({
            factor: item.feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            importance: item.importance
          }));
        }

        console.log('Dashboard SHAP data:', transformedShapData);

        // Combine data into dashboardData
        const combinedDashboardData = {
          summary: {
            total_patients: summaryData?.totalPatients || 0,
            total_predictions: summaryData?.totalPredictions || 0,
            recent_predictions: summaryData?.recentPredictions || 0,
            low_risk_count: riskData?.low || 0,
            medium_risk_count: riskData?.medium || 0,
            high_risk_count: riskData?.high || 0,
          },
          risk_distribution: {
            LOW: riskData?.low || 0,
            MEDIUM: riskData?.medium || 0,
            HIGH: riskData?.high || 0,
          },
          top_risk_factors: transformedShapData,
          alerts_summary: [],
        };

        setDashboardData(combinedDashboardData);
        if (demographicsData) {
          setDemographicsData(demographicsData);
        }
        setLoading(false);
      } catch (err) {
        setError('Failed to load dashboard data');
        setLoading(false);
        console.error('Error fetching dashboard data:', err);
      }
    };

    fetchData();
  }, []);

  // Prepare chart data
  const riskDistributionData = {
    labels: ['Low Risk', 'Medium Risk', 'High Risk'],
    datasets: [
      {
        data: [
          dashboardData?.summary?.low_risk_count || 0,
          dashboardData?.summary?.medium_risk_count || 0,
          dashboardData?.summary?.high_risk_count || 0
        ],
        backgroundColor: ['#4CAF50', '#FF9800', '#F44336'],
        borderColor: ['#388E3C', '#F57C00', '#D32F2F'],
        borderWidth: 1,
      }
    ]
  };

  const topRiskFactorsData = {
    labels: dashboardData?.top_risk_factors?.slice(0, 5)?.map(item => item.factor) || [],
    datasets: [
      {
        label: 'Factor Importance',
        data: dashboardData?.top_risk_factors?.slice(0, 5)?.map(item => item.importance) || [],
        backgroundColor: '#6C7CFF',
        borderColor: '#4F46E5',
        borderWidth: 1,
      }
    ]
  };

  const ageDistributionData = {
    labels: ['0-30', '31-50', '51-70', '71+'],
    datasets: [
      {
        label: 'Patient Count',
        data: [
          demographicsData?.age_distribution?.['0-30'] || 0,
          demographicsData?.age_distribution?.['31-50'] || 0,
          demographicsData?.age_distribution?.['51-70'] || 0,
          demographicsData?.age_distribution?.['71+'] || 0
        ],
        backgroundColor: ['#6C7CFF', '#A78BFA', '#38BDF8', '#F59E0B'],
        borderColor: ['#4F46E5', '#8B5CF6', '#0EA5E9', '#D97706'],
        borderWidth: 1,
      }
    ]
  };

  const genderDistributionData = {
    labels: ['Male', 'Female', 'Other'],
    datasets: [
      {
        data: [
          demographicsData?.gender_distribution?.Male || 0,
          demographicsData?.gender_distribution?.Female || 0,
          demographicsData?.gender_distribution?.Other || 0
        ],
        backgroundColor: ['#5B8CFF', '#9B7EDE', '#4FC3F7'],
        borderColor: ['#4F46E5', '#8B5CF6', '#0EA5E9'],
        borderWidth: 1,
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            return `${context.label}: ${context.parsed}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      },
      x: {
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      }
    }
  };

  const riskDistributionOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            return `${context.label}: ${context.parsed}`;
          }
        }
      }
    },
    cutout: '60%', // Creates donut chart
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      },
      x: {
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      }
    }
  };

  const shapOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            return `${context.label}: ${context.parsed}`;
          }
        }
      }
    },
    indexAxis: 'y',
    scales: {
      ...chartOptions.scales,
      x: {
        ...chartOptions.scales.x,
        title: {
          display: true,
          text: 'Importance Score'
        }
      }
    }
  };

  const genderOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            const total = context.dataset.data.reduce((sum, value) => sum + value, 0);
            const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0;
            return `${context.label}: ${context.parsed} (${percentage}%)`;
          }
        }
      }
    },
    cutout: '60%', // Creates donut chart
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      },
      x: {
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      }
    }
  };

  if (loading) {
    return (
      <DashboardContainer>
        <ContentWrapper>
          <div style={{ gridColumn: '1 / -1', display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
            Loading dashboard...
          </div>
        </ContentWrapper>
      </DashboardContainer>
    );
  }

  if (error) {
    return (
      <DashboardContainer>
        <ContentWrapper>
          <div style={{ gridColumn: '1 / -1', display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
            {error}
          </div>
        </ContentWrapper>
      </DashboardContainer>
    );
  }

  return (
    <DashboardContainer>
      <ContentWrapper>
        <Header>
          <DashboardTitle>Clinical Dashboard</DashboardTitle>
          <Subtitle>Overview of patient risk assessments and system analytics</Subtitle>
        </Header>

        <StatsGrid>
          <StatCard>
            <StatValue>{dashboardData?.summary?.total_patients || 0}</StatValue>
            <StatLabel>Total Patients</StatLabel>
          </StatCard>

          <StatCard>
            <StatValue>{dashboardData?.summary?.total_predictions || 0}</StatValue>
            <StatLabel>Total Predictions</StatLabel>
          </StatCard>

          <StatCard>
            <StatValue>{dashboardData?.summary?.recent_predictions || 0}</StatValue>
            <StatLabel>Recent Predictions</StatLabel>
          </StatCard>

          <StatCard>
            <StatValue>{dashboardData?.summary?.high_risk_count || 0}</StatValue>
            <StatLabel>High Risk Cases</StatLabel>
          </StatCard>
        </StatsGrid>

        <ChartsGrid>
          <ChartCard>
            <ChartTitle>Population Risk Distribution</ChartTitle>
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
              <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {dashboardData?.summary?.total_patients > 0 ? (
                  <Pie data={riskDistributionData} options={{
                    ...riskDistributionOptions,
                    maintainAspectRatio: false,
                    responsive: true
                  }} />
                ) : (
                  <div style={{ textAlign: 'center', color: '#6B7280', fontSize: '14px' }}>
                    No patient data available yet
                  </div>
                )}
              </div>
            </div>
          </ChartCard>

          <ChartCard>
            <ChartTitle>Top Risk Factors (SHAP)</ChartTitle>
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
              <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {dashboardData?.top_risk_factors && dashboardData.top_risk_factors.length > 0 ? (
                  <Bar
                    data={topRiskFactorsData}
                    options={{
                      ...shapOptions,
                      maintainAspectRatio: false,
                      responsive: true
                    }}
                  />
                ) : (
                  <div style={{ textAlign: 'center', color: '#6B7280', fontSize: '14px' }}>
                    {dashboardData?.summary?.total_predictions > 0 
                      ? 'SHAP data not available for recent predictions' 
                      : 'SHAP explanation available after first prediction'}
                  </div>
                )}
              </div>
            </div>
          </ChartCard>
        </ChartsGrid>

        <div style={{ gridColumn: '1 / -1', display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gridColumnGap: '24px', gridRowGap: '32px' }}>
          <ChartCard>
            <ChartTitle>Age Distribution</ChartTitle>
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
              <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {demographicsData?.patient_list && demographicsData.patient_list.length > 0 ? (
                  <Bar data={ageDistributionData} options={{
                    ...chartOptions,
                    maintainAspectRatio: false,
                    responsive: true
                  }} />
                ) : (
                  <div style={{ textAlign: 'center', color: '#6B7280', fontSize: '14px' }}>
                    No patient data available yet
                  </div>
                )}
              </div>
            </div>
          </ChartCard>

          <ChartCard>
            <ChartTitle>Gender Distribution</ChartTitle>
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
              <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {demographicsData?.gender_distribution && (demographicsData.gender_distribution.Male > 0 || demographicsData.gender_distribution.Female > 0 || demographicsData.gender_distribution.Other > 0) ? (
                  <Pie
                    data={genderDistributionData}
                    options={{
                      ...genderOptions,
                      maintainAspectRatio: false,
                      responsive: true
                    }}
                  />
                ) : (
                  <div style={{ textAlign: 'center', color: '#6B7280', fontSize: '14px' }}>
                    No patient data available yet
                  </div>
                )}
              </div>
            </div>
          </ChartCard>
        </div>

        {dashboardData?.alerts_summary && dashboardData.alerts_summary.length > 0 && (
          <AlertsContainer>
            <AlertsTitle>Priority Alerts</AlertsTitle>
            {dashboardData.alerts_summary.map((alert, index) => (
              <AlertItem key={index}>
                <AlertText>
                  Patient: {alert.patient_id} • {alert.factors.join(', ')}
                </AlertText>
                <AlertRisk level="HIGH">
                  {Math.round(alert.risk_score * 100)}% Risk
                </AlertRisk>
              </AlertItem>
            ))}
          </AlertsContainer>
        )}
      </ContentWrapper>
    </DashboardContainer>
  );
};

export default DashboardPage;