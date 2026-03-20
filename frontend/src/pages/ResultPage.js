import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title as ChartTitle,
  Tooltip,
  Legend
} from 'chart.js';
import styled from 'styled-components';
import axios from 'axios';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  ChartTitle,
  Tooltip,
  Legend
);

const ResultContainer = styled.div`
  min-height: 100vh;
  background-color: #EEF1F5;
  padding: 24px;
`;

const ContentWrapper = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 40px;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 20px;
`;

const Title = styled.h1`
  color: #1F2937;
  font-size: 32px;
  margin-bottom: 12px;
`;

const Subtitle = styled.p`
  color: #6B7280;
  font-size: 16px;
  max-width: 800px;
  margin: 0 auto;
`;

const SectionTitle = styled.h2`
  color: #1F2937;
  font-size: 24px;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #E5E7EB;
`;

const GridRow = styled.div`
  display: grid;
  grid-template-columns: repeat(${props => props.columns || 2}, 1fr);
  gap: 30px;
  margin-bottom: 20px;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled.div`
  background: #FFFFFF;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  min-height: 400px;
`;

const ChartContainer = styled.div`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  min-height: 300px;
`;

const VisualizationImage = styled.img`
  max-width: 100%;
  max-height: 350px;
  object-fit: contain;
`;

const RiskBadge = styled.span`
  background-color: ${props => props.color};
  color: white;
  padding: 4px 12px;
  border-radius: 9999px;
  font-weight: 500;
  font-size: 14px;
`;

const ActionButtons = styled.div`
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
`;

const Button = styled.button`
  background: #6C7CFF;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: #5A6AE6;
    transform: translateY(-2px);
  }
`;

const ResultPage = () => {
  const { predictionId } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState({
    prediction: null,
    dashboard: null,
    shapImage: null,
    glucoseImage: null,
    scanAnalysis: null
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('authToken');
        const config = { headers: { Authorization: `Bearer ${token}` } };
        const baseUrl = process.env.REACT_APP_API_URL || '';

        // 1. Fetch Prediction Data
        const predRes = await axios.get(`${baseUrl}/api/predictions/${predictionId}`, config);

        // 2. Fetch Dashboard Summary (for Row 3)
        const dashRes = await Promise.all([
          axios.get(`${baseUrl}/api/dashboard/patients`, config).catch(() => ({ data: null })),
          axios.get(`${baseUrl}/api/dashboard/risk-distribution`, config).catch(() => ({ data: null }))
        ]);

        // 3. Fetch Dynamic Visualizations (All images via API)
        const vizRes = await Promise.all([
          axios.get(`${baseUrl}/api/predictions/${predictionId}/visualizations/shap`, config).catch(() => null),
          axios.get(`${baseUrl}/api/predictions/${predictionId}/visualizations/glucose`, config).catch(() => null),
          axios.get(`${baseUrl}/api/model/visualizations/heatmap`, config).catch(() => null),
          axios.get(`${baseUrl}/api/model/visualizations/confusion-matrix`, config).catch(() => null)
        ]);
        
        // 4. Fetch Scan Analysis
        const scanAnalysisRes = await axios.get(`${baseUrl}/api/predictions/${predictionId}/scan-analysis`, config).catch(() => null);

        setData({
          prediction: predRes.data,
          dashboard: {
            demographics: dashRes[0].data,
            risk: dashRes[1].data
          },
          shapImage: vizRes[0]?.data?.image ? `data:image/png;base64,${vizRes[0].data.image}` : null,
          glucoseImage: vizRes[1]?.data?.image ? `data:image/png;base64,${vizRes[1].data.image}` : null,
          heatmapImage: vizRes[2]?.data?.image ? `data:image/png;base64,${vizRes[2].data.image}` : null,
          confusionImage: vizRes[3]?.data?.image ? `data:image/png;base64,${vizRes[3].data.image}` : null,
          scanAnalysis: scanAnalysisRes?.data || null
        });

        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        const msg = err.response?.data?.error || err.response?.data?.message || err.message || 'Failed to load analysis data';
        setError(msg);
        setLoading(false);
      }
    };

    if (predictionId) fetchData();
  }, [predictionId]);

  if (loading) return <ResultContainer><div className="flex-center">Loading comprehensive analysis...</div></ResultContainer>;
  if (error) return <ResultContainer><div className="flex-center">{error}</div></ResultContainer>;

  // Helper for charts
  const getRiskColor = (score) => {
    if (score < 0.3) return '#22C55E';
    if (score < 0.6) return '#F59E0B';
    return '#EF4444';
  };

  const riskScore = data.prediction?.risk_score || 0;
  const riskColor = getRiskColor(riskScore);

  // Row 3 Charts Data
  const ageData = {
    labels: ['0-30', '31-50', '51-70', '71+'],
    datasets: [{
      label: 'Patients',
      data: Object.values(data.dashboard?.demographics?.age_distribution || {}),
      backgroundColor: '#6C7CFF'
    }]
  };

  const genderData = {
    labels: Object.keys(data.dashboard?.demographics?.gender_distribution || {}),
    datasets: [{
      data: Object.values(data.dashboard?.demographics?.gender_distribution || {}),
      backgroundColor: ['#6C7CFF', '#F472B6', '#9CA3AF']
    }]
  };

  const riskDistData = {
    labels: ['Low', 'Medium', 'High'],
    datasets: [{
      data: [
        data.dashboard?.risk?.low || 0,
        data.dashboard?.risk?.medium || 0,
        data.dashboard?.risk?.high || 0
      ],
      backgroundColor: ['#22C55E', '#F59E0B', '#EF4444']
    }]
  };

  return (
    <ResultContainer>
      <ContentWrapper>
        <Header>
          <RiskBadge color={riskColor}>{Math.round(riskScore * 100)}% Risk Score</RiskBadge>
          <Title>Advanced Clinical Analysis</Title>
          <Subtitle>
            Analysis for {data.prediction?.patient?.full_name || 'Patient'} •
            Model Confidence: v{data.prediction?.model_version || '2.0.0'}
          </Subtitle>
        </Header>

        {/* Row 1: Patient Analysis */}
        <div>
          <SectionTitle>Row 1: Patient Analysis</SectionTitle>
          <GridRow columns={2}>
            <Card>
              <h3>SHAP Risk Driver Analysis</h3>
              <ChartContainer>
                {data.shapImage ? (
                  <VisualizationImage src={data.shapImage} alt="SHAP Plot" />
                ) : (
                  <p>Generating interpretation...</p>
                )}
              </ChartContainer>
            </Card>
            <Card>
              <h3>Glucose Clinical Impact</h3>
              <ChartContainer>
                {data.glucoseImage ? (
                  <VisualizationImage src={data.glucoseImage} alt="Glucose Plot" />
                ) : (
                  <p>Generating clinical comparison...</p>
                )}
              </ChartContainer>
            </Card>
          </GridRow>
        </div>

        {/* Row 2: Model Evaluation */}
        <div>
          <SectionTitle>Row 2: Model Evaluation</SectionTitle>
          <GridRow columns={2}>
            <Card>
              <h3>Feature Correlation Heatmap</h3>
              <ChartContainer>
                {data.heatmapImage ? (
                  <VisualizationImage
                    src={data.heatmapImage}
                    alt="Correlation Heatmap"
                  />
                ) : (
                  <p>Loading heatmap...</p>
                )}
              </ChartContainer>
            </Card>
            <Card>
              <h3>Model Confusion Matrix</h3>
              <ChartContainer>
                {data.confusionImage ? (
                  <VisualizationImage
                    src={data.confusionImage}
                    alt="Confusion Matrix"
                  />
                ) : (
                  <p>Loading confusion matrix...</p>
                )}
              </ChartContainer>
            </Card>
          </GridRow>
        </div>

        {/* Row 3: Dataset Overview */}
        <div>
          <SectionTitle>Row 3: Dataset Overview</SectionTitle>
          <GridRow columns={3}>
            <Card>
              <h3>Age Distribution</h3>
              <ChartContainer>
                <Bar
                  data={ageData}
                  options={{ responsive: true, maintainAspectRatio: false }}
                />
              </ChartContainer>
            </Card>
            <Card>
              <h3>Gender Distribution</h3>
              <ChartContainer>
                <Pie
                  data={genderData}
                  options={{ responsive: true, maintainAspectRatio: false }}
                />
              </ChartContainer>
            </Card>
            <Card>
              <h3>Population Risk</h3>
              <ChartContainer>
                <Pie
                  data={riskDistData}
                  options={{ responsive: true, maintainAspectRatio: false }}
                />
              </ChartContainer>
            </Card>
          </GridRow>
        </div>

        {/* Scan Analysis Section */}
        {data.scanAnalysis && (
          <div>
            <SectionTitle>Scan Analysis Results</SectionTitle>
            <GridRow columns={2}>
              <Card>
                <h3>Imaging Findings</h3>
                <div style={{ marginTop: '20px' }}>
                  <p><strong>Scan Type:</strong> {data.scanAnalysis.modality || 'Unknown'}</p>
                  <p><strong>Scan Quality:</strong> {data.scanAnalysis.scan_valid ? 'Valid' : 'Invalid'}</p>
                  <p><strong>AI Prediction:</strong> {data.scanAnalysis.dl_prediction}</p>
                  <p><strong>Confidence:</strong> {(data.scanAnalysis.dl_confidence * 100).toFixed(1)}%</p>
                  <p><strong>Stroke Risk:</strong> {(data.scanAnalysis.stroke_risk * 100).toFixed(1)}%</p>
                </div>
              </Card>
              <Card>
                <h3>Detailed Findings</h3>
                <div style={{ marginTop: '20px' }}>
                  <h4 style={{ color: '#6C7CFF', marginBottom: '10px' }}>Clinical Observations:</h4>
                  <ul>
                    {data.scanAnalysis.findings && data.scanAnalysis.findings.map((finding, index) => (
                      <li key={index} style={{ marginBottom: '8px', lineHeight: '1.5' }}>
                        • {finding}
                      </li>
                    ))}
                  </ul>
                  <h4 style={{ color: '#6C7CFF', marginBottom: '10px', marginTop: '20px' }}>Recommendations:</h4>
                  <ul>
                    {data.scanAnalysis.recommendations && data.scanAnalysis.recommendations.map((rec, index) => (
                      <li key={index} style={{ marginBottom: '8px', lineHeight: '1.5' }}>
                        • {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              </Card>
            </GridRow>
          </div>
        )}

        <ActionButtons>
          <Button onClick={() => navigate('/prediction')}>New Prediction</Button>
          <Button onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
        </ActionButtons>

      </ContentWrapper>
    </ResultContainer>
  );
};

export default ResultPage;