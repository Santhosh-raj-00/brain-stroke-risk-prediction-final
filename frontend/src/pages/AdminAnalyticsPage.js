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

const AdminAnalyticsContainer = styled.div`
  min-height: 100vh;
  background-color: #ECEFF4;
  padding: 20px;
`;

const ContentWrapper = styled.div`
  max-width: 1400px;
  margin: 0 auto;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 40px;
`;

const PageTitle = styled.h1`
  color: #1F2937;
  font-size: 32px;
  margin-bottom: 12px;
`;

const Subtitle = styled.p`
  color: #6B7280;
  font-size: 16px;
  max-width: 600px;
  margin: 0 auto;
`;

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
`;

const SmallChartsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
`;

const ChartCard = styled.div`
  background: #F6F8FB;
  border-radius: 16px;
  padding: 24px;
  box-shadow:
    8px 8px 18px #D1D9E6,
    -8px -8px 18px #FFFFFF;
`;

const ChartTitle = styled.h3`
  color: #1F2937;
  font-size: 16px;
  margin-bottom: 20px;
  text-align: center;
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
`;

const MetricCard = styled.div`
  background: #F6F8FB;
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  box-shadow:
    8px 8px 18px #D1D9E6,
    -8px -8px 18px #FFFFFF;
`;

const MetricValue = styled.div`
  font-size: 24px;
  font-weight: 700;
  color: #6C7CFF;
  margin-bottom: 8px;
`;

const MetricLabel = styled.div`
  color: #6B7280;
  font-size: 14px;
`;

const AdminAnalyticsPage = () => {
  const [metrics, setMetrics] = useState(null);
  const [shapSummary, setShapSummary] = useState(null);
  const [errorAnalysis, setErrorAnalysis] = useState(null);
  const [thresholdAnalysis, setThresholdAnalysis] = useState(null);
  const [modelPerformance, setModelPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const responses = await Promise.allSettled([
          axios.get(
            `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/admin/ml-metrics`,
            {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
              }
            }
          ),
          axios.get(
            `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/admin/shap-summary`,
            {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
              }
            }
          ),
          axios.get(
            `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/admin/error-analysis`,
            {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
              }
            }
          ),
          axios.get(
            `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/admin/threshold-analysis`,
            {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
              }
            }
          ),
          axios.get(
            `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/admin/model-performance`,
            {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
              }
            }
          )
        ]);

        // Process responses
        const [metricsRes, shapRes, errorRes, thresholdRes, modelRes] = responses;
        
        if (metricsRes.status === 'fulfilled') {
          setMetrics(metricsRes.value.data);
        }
        if (shapRes.status === 'fulfilled') {
          setShapSummary(shapRes.value.data);
        }
        if (errorRes.status === 'fulfilled') {
          setErrorAnalysis(errorRes.value.data);
        }
        if (thresholdRes.status === 'fulfilled') {
          setThresholdAnalysis(thresholdRes.value.data);
        }
        if (modelRes.status === 'fulfilled') {
          setModelPerformance(modelRes.value.data);
        }

        setLoading(false);
      } catch (err) {
        setError('Failed to load analytics data');
        setLoading(false);
        console.error('Error fetching admin analytics:', err);
      }
    };

    fetchData();
  }, []);

  // Prepare chart data
  const riskDistributionData = {
    labels: ['Low Risk', 'Medium Risk', 'High Risk'],
    datasets: [
      {
        label: 'Prediction Count',
        data: [
          metrics?.risk_distribution?.LOW || 0,
          metrics?.risk_distribution?.MEDIUM || 0,
          metrics?.risk_distribution?.HIGH || 0
        ],
        backgroundColor: ['#22C55E', '#F59E0B', '#EF4444'],
        borderColor: ['#16A34A', '#D97706', '#DC2626'],
        borderWidth: 1,
      }
    ]
  };

  const featureImportanceData = {
    labels: shapSummary?.feature_importance 
      ? Object.keys(shapSummary.feature_importance).slice(0, 10) 
      : [],
    datasets: [
      {
        label: 'Average Importance',
        data: shapSummary?.feature_importance 
          ? Object.values(shapSummary.feature_importance).slice(0, 10).map(f => f.avg_importance) 
          : [],
        backgroundColor: '#6C7CFF',
        borderColor: '#4F46E5',
        borderWidth: 1,
      }
    ]
  };

  const modelPerformanceData = {
    labels: modelPerformance?.model_versions 
      ? Object.keys(modelPerformance.model_versions) 
      : [],
    datasets: [
      {
        label: 'Average Risk Score',
        data: modelPerformance?.model_versions 
          ? Object.values(modelPerformance.model_versions).map(v => v.average_risk_score) 
          : [],
        backgroundColor: '#A78BFA',
        borderColor: '#8B5CF6',
        borderWidth: 1,
      }
    ]
  };

  const thresholdData = {
    labels: thresholdAnalysis?.threshold_scenarios 
      ? Object.keys(thresholdAnalysis.threshold_scenarios).slice(0, 5) 
      : [],
    datasets: [
      {
        label: 'Low %',
        data: thresholdAnalysis?.threshold_scenarios 
          ? Object.values(thresholdAnalysis.threshold_scenarios).slice(0, 5).map(t => t.percentages.LOW) 
          : [],
        backgroundColor: 'rgba(34, 197, 94, 0.5)',
      },
      {
        label: 'Medium %',
        data: thresholdAnalysis?.threshold_scenarios 
          ? Object.values(thresholdAnalysis.threshold_scenarios).slice(0, 5).map(t => t.percentages.MEDIUM) 
          : [],
        backgroundColor: 'rgba(245, 158, 11, 0.5)',
      },
      {
        label: 'High %',
        data: thresholdAnalysis?.threshold_scenarios 
          ? Object.values(thresholdAnalysis.threshold_scenarios).slice(0, 5).map(t => t.percentages.HIGH) 
          : [],
        backgroundColor: 'rgba(239, 68, 68, 0.5)',
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: ${context.parsed.y}`;
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

  if (loading) {
    return (
      <AdminAnalyticsContainer>
        <ContentWrapper>
          <div className="flex-center">Loading analytics...</div>
        </ContentWrapper>
      </AdminAnalyticsContainer>
    );
  }

  if (error) {
    return (
      <AdminAnalyticsContainer>
        <ContentWrapper>
          <div className="flex-center">{error}</div>
        </ContentWrapper>
      </AdminAnalyticsContainer>
    );
  }

  return (
    <AdminAnalyticsContainer>
      <ContentWrapper>
        <Header>
          <PageTitle>Admin ML Analytics</PageTitle>
          <Subtitle>Comprehensive machine learning model performance and system analytics</Subtitle>
        </Header>
        
        <MetricsGrid>
          <MetricCard>
            <MetricValue>{metrics?.total_predictions || 0}</MetricValue>
            <MetricLabel>Total Predictions</MetricLabel>
          </MetricCard>
          
          <MetricCard>
            <MetricValue>{metrics?.statistical_measures?.average_risk_score ? 
              (metrics.statistical_measures.average_risk_score * 100).toFixed(1) + '%' : 'N/A'}</MetricValue>
            <MetricLabel>Avg Risk Score</MetricLabel>
          </MetricCard>
          
          <MetricCard>
            <MetricValue>{metrics?.statistical_measures?.std_deviation ? 
              metrics.statistical_measures.std_deviation.toFixed(2) : 'N/A'}</MetricValue>
            <MetricLabel>Std Deviation</MetricLabel>
          </MetricCard>
          
          <MetricCard>
            <MetricValue>{Object.keys(modelPerformance?.model_versions || {}).length}</MetricValue>
            <MetricLabel>Model Versions</MetricLabel>
          </MetricCard>
        </MetricsGrid>
        
        <ChartsGrid>
          <ChartCard>
            <ChartTitle>Population Risk Distribution</ChartTitle>
            <Bar data={riskDistributionData} options={chartOptions} />
          </ChartCard>
          
          <ChartCard>
            <ChartTitle>Feature Importance (SHAP)</ChartTitle>
            <Bar 
              data={featureImportanceData} 
              options={{
                ...chartOptions,
                indexAxis: 'y',
                scales: {
                  ...chartOptions.scales,
                  x: {
                    ...chartOptions.scales.x,
                    title: {
                      display: true,
                      text: 'Average SHAP Value'
                    }
                  }
                }
              }} 
            />
          </ChartCard>
        </ChartsGrid>
        
        <SmallChartsGrid>
          <ChartCard>
            <ChartTitle>Model Performance by Version</ChartTitle>
            <Bar data={modelPerformanceData} options={chartOptions} />
          </ChartCard>
          
          <ChartCard>
            <ChartTitle>Threshold Analysis</ChartTitle>
            <Bar data={thresholdData} options={chartOptions} />
          </ChartCard>
        </SmallChartsGrid>
        
        <ChartsGrid>
          <ChartCard>
            <ChartTitle>High-Risk Pattern Analysis</ChartTitle>
            <Bar 
              data={{
                labels: errorAnalysis?.high_risk_patterns 
                  ? Object.keys(errorAnalysis.high_risk_patterns).slice(0, 8) 
                  : [],
                datasets: [
                  {
                    label: 'Mean Value',
                    data: errorAnalysis?.high_risk_patterns 
                      ? Object.values(errorAnalysis.high_risk_patterns).slice(0, 8).map(p => p.mean_value) 
                      : [],
                    backgroundColor: '#F59E0B',
                    borderColor: '#D97706',
                    borderWidth: 1,
                  }
                ]
              }} 
              options={chartOptions} 
            />
          </ChartCard>
          
          <ChartCard>
            <ChartTitle>Model Version Comparison</ChartTitle>
            <Pie 
              data={{
                labels: modelPerformance?.model_versions 
                  ? Object.keys(modelPerformance.model_versions) 
                  : [],
                datasets: [
                  {
                    data: modelPerformance?.model_versions 
                      ? Object.values(modelPerformance.model_versions).map(v => v.total_predictions) 
                      : [],
                    backgroundColor: ['#6C7CFF', '#A78BFA', '#38BDF8', '#F59E0B', '#EF4444'],
                    borderColor: ['#4F46E5', '#8B5CF6', '#0EA5E9', '#D97706', '#DC2626'],
                    borderWidth: 1,
                  }
                ]
              }} 
              options={chartOptions} 
            />
          </ChartCard>
        </ChartsGrid>
      </ContentWrapper>
    </AdminAnalyticsContainer>
  );
};

export default AdminAnalyticsPage;