import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import styled from 'styled-components';
import axios from 'axios';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const HistoryContainer = styled.div`
  min-height: 100vh;
  background-color: #EEF1F5;
  padding: 20px;
`;

const ContentWrapper = styled.div`
  max-width: 1200px;
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

const FiltersContainer = styled.div`
  background: #F6F8FB;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow:
    8px 8px 18px #D1D9E6,
    -8px -8px 18px #FFFFFF;
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
`;

const FilterSelect = styled.select`
  padding: 12px 16px;
  border: none;
  border-radius: 16px;
  background: #F6F8FB;
  color: #1F2937;
  font-size: 14px;
  box-shadow:
    inset 4px 4px 8px #D1D9E6,
    inset -4px -4px 8px #FFFFFF;
  outline: none;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231F2937' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 1em;
  flex: 1;
  min-width: 200px;
  
  &:focus {
    box-shadow:
      inset 6px 6px 12px #D1D9E6,
      inset -6px -6px 12px #FFFFFF;
  }
`;

const TimelineContainer = styled.div`
  background: #F6F8FB;
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 40px;
  box-shadow:
    8px 8px 18px #D1D9E6,
    -8px -8px 18px #FFFFFF;
`;

const TimelineItem = styled.div`
  display: flex;
  padding: 16px 0;
  border-bottom: 1px solid #E5E7EB;
  
  &:last-child {
    border-bottom: none;
  }
`;

const TimelineDate = styled.div`
  min-width: 150px;
  color: #6B7280;
  font-size: 14px;
  font-weight: 500;
`;

const TimelineContent = styled.div`
  flex: 1;
`;

const TimelineRisk = styled.div`
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
  color: ${props => {
    if (props.risk <= 0.2) return '#22C55E';
    if (props.risk <= 0.6) return '#F59E0B';
    return '#EF4444';
  }};
`;

const TimelinePatient = styled.div`
  color: #1F2937;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 4px;
`;

const TimelineDoctor = styled.div`
  color: #6B7280;
  font-size: 14px;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 8px;
`;

const Button = styled.button`
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  background: ${props => props.variant === 'primary' ? '#6C7CFF' : '#EF4444'};
  color: white;
  font-size: 12px;
  cursor: pointer;
  box-shadow:
    4px 4px 8px rgba(108, 124, 255, 0.2),
    -4px -4px 8px rgba(255, 255, 255, 0.6);
  transition: all 0.3s ease;

  &:hover {
    opacity: 0.9;
    transform: translateY(-1px);
  }
`;

const ChartsContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: 30px;
  margin-bottom: 40px;
`;

const ChartCard = styled.div`
  background: #F6F8FB;
  border-radius: 20px;
  padding: 30px;
  box-shadow:
    8px 8px 18px #D1D9E6,
    -8px -8px 18px #FFFFFF;
`;

const ChartTitle = styled.h3`
  color: #1F2937;
  font-size: 18px;
  margin-bottom: 20px;
  text-align: center;
`;

const HistoryPage = () => {
  const location = useLocation();
  const [history, setHistory] = useState([]);
  const [filteredHistory, setFilteredHistory] = useState([]);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [filters, setFilters] = useState({
    patient: '',
    risk: '',
    dateFrom: '',
    dateTo: ''
  });
  
  // Extract patient_id from query parameters
  const urlParams = new URLSearchParams(location.search);
  const patientId = urlParams.get('patient_id');

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        // Use relative path for proxy configuration
        const apiUrl = process.env.REACT_APP_API_URL;
        const baseUrl = apiUrl && apiUrl !== '/' ? `${apiUrl}/api/history` : '/api/history';
        const historyUrl = patientId ? `${baseUrl}?patient_id=${patientId}` : baseUrl;
        
        const response = await axios.get(
          historyUrl,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
          }
        );
        
        setHistory(response.data);
        setFilteredHistory(response.data);
        
        // Also fetch trends for charts
        if (response.data.length > 0) {
          // Group by patient and get the first patient's trends
          const firstPatientId = response.data[0].patient_id;
          // Use relative path for proxy configuration
          const apiUrl = process.env.REACT_APP_API_URL;
          const trendsUrl = apiUrl && apiUrl !== '/' ? `${apiUrl}/api/history/trends?patient_id=${firstPatientId}` : `/api/history/trends?patient_id=${firstPatientId}`;
          
          const trendResponse = await axios.get(
            trendsUrl,
            {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
              }
            }
          );
          setTrends(trendResponse.data.trends || []);
        }
        
        setLoading(false);
      } catch (err) {
        setError('Failed to load history');
        setLoading(false);
        console.error('Error fetching history:', err);
      }
    };

    fetchHistory();
  }, [patientId]);

  const downloadPDF = async (predictionId) => {
    try {
      console.log('Downloading PDF for prediction:', predictionId);
      
      // Use relative path for proxy configuration
      const apiUrl = process.env.REACT_APP_API_URL;
      const url = apiUrl && apiUrl !== '/' ? `${apiUrl}/api/predictions/${predictionId}/pdf` : `/api/predictions/${predictionId}/pdf`;
      
      console.log('Request URL:', url);
      
      const response = await axios.get(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        responseType: 'blob' // Important: specify blob response type
      });
      
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);
      
      // Check if response is actually a PDF
      const contentType = response.headers['content-type'];
      if (!contentType || !contentType.includes('application/pdf')) {
        console.error('Invalid content type:', contentType);
        setError('Failed to download PDF: Invalid response type');
        return;
      }
      
      // Create a temporary URL for the blob and trigger download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const downloadUrl = window.URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.setAttribute('download', `prediction-report-${predictionId}.pdf`);
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);
      
      console.log('PDF download completed');
    } catch (error) {
      console.error('Error downloading PDF:', error);
      console.error('Error response:', error.response);
      
      if (error.response) {
        console.error('Status:', error.response.status);
        console.error('Data:', error.response.data);
        
        // Try to parse error message
        let errorMsg = 'Failed to download PDF report';
        if (error.response.data) {
          if (typeof error.response.data === 'string') {
            errorMsg = error.response.data;
          } else if (error.response.data.error) {
            errorMsg = error.response.data.error;
          }
        }
        setError(errorMsg);
      } else {
        setError('Network error: Could not connect to server');
      }
    }
  };

  const deleteRecord = async (predictionId) => {
    if (window.confirm('Are you sure you want to delete this prediction record? This action cannot be undone.')) {
      try {
        // Use relative path for proxy configuration
        const apiUrl = process.env.REACT_APP_API_URL;
        const url = apiUrl && apiUrl !== '/' ? `${apiUrl}/api/predictions/${predictionId}` : `/api/predictions/${predictionId}`;
        
        await axios.delete(url, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
          }
        });
        
        // Refresh the history after deletion
        const apiUrl2 = process.env.REACT_APP_API_URL;
        const baseUrl = apiUrl2 && apiUrl2 !== '/' ? `${apiUrl2}/api/history` : '/api/history';
        const historyUrl = patientId ? `${baseUrl}?patient_id=${patientId}` : baseUrl;
        
        const response = await axios.get(
          historyUrl,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
          }
        );
        
        setHistory(response.data);
      } catch (error) {
        console.error('Error deleting record:', error);
        setError('Failed to delete prediction record');
      }
    }
  };

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  // Apply filters when history or filters change
  useEffect(() => {
    let result = [...history];
    
    // Apply risk filter
    if (filters.risk) {
      result = result.filter(item => 
        item.risk_category === filters.risk
      );
    }
    
    // Apply date range filter
    if (filters.dateFrom) {
      result = result.filter(item => {
        try {
          return new Date(item.created_at) >= new Date(filters.dateFrom);
        } catch {
          return false;
        }
      });
    }
    
    if (filters.dateTo) {
      result = result.filter(item => {
        try {
          return new Date(item.created_at) <= new Date(filters.dateTo);
        } catch {
          return false;
        }
      });
    }
    
    setFilteredHistory(result);
  }, [history, filters]);

  // Prepare chart data
  const riskTrendData = {
    labels: trends.map(item => {
      try {
        return new Date(item.date).toLocaleDateString();
      } catch {
        return 'Invalid Date';
      }
    }),
    datasets: [
      {
        label: 'Risk Score Trend',
        data: trends.map(item => {
          try {
            return Math.round(item.risk_score * 100);
          } catch {
            return 0;
          }
        }),
        borderColor: '#6C7CFF',
        backgroundColor: 'rgba(108, 124, 255, 0.1)',
        tension: 0.4,
        fill: true,
      }
    ]
  };

  const glucoseTrendData = {
    labels: trends.map(item => new Date(item.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Glucose Level',
        data: trends.map(item => {
          if (item.input_features && typeof item.input_features === 'object') {
            return parseFloat(item.input_features.avg_glucose_level) || 0;
          }
          return 0;
        }),
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
        fill: true,
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
        beginAtZero: false,
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
      <HistoryContainer>
        <ContentWrapper>
          <div className="flex-center">Loading history...</div>
        </ContentWrapper>
      </HistoryContainer>
    );
  }

  if (error) {
    return (
      <HistoryContainer>
        <ContentWrapper>
          <div className="flex-center">{error}</div>
        </ContentWrapper>
      </HistoryContainer>
    );
  }

  return (
    <HistoryContainer>
      <ContentWrapper>
        <Header>
          <PageTitle>{patientId ? 'Patient History' : 'Prediction History'}</PageTitle>
          <Subtitle>
            {patientId 
              ? 'Viewing history for specific patient' 
              : 'Track prediction timeline and patient risk trends'
            }
          </Subtitle>
        </Header>
        
        <FiltersContainer>
          <FilterSelect 
            value={filters.patient} 
            onChange={(e) => handleFilterChange('patient', e.target.value)}
          >
            <option value="">All Patients</option>
            {/* Would populate with actual patient list */}
          </FilterSelect>
          
          <FilterSelect 
            value={filters.risk} 
            onChange={(e) => handleFilterChange('risk', e.target.value)}
          >
            <option value="">All Risk Levels</option>
            <option value="LOW">Low Risk</option>
            <option value="MEDIUM">Medium Risk</option>
            <option value="HIGH">High Risk</option>
          </FilterSelect>
          
          <input
            type="date"
            value={filters.dateFrom}
            onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
            style={{
              padding: '12px 16px',
              border: 'none',
              borderRadius: '16px',
              background: '#F6F8FB',
              color: '#1F2937',
              fontSize: '14px',
              boxShadow: 'inset 4px 4px 8px #D1D9E6, inset -4px -4px 8px #FFFFFF',
              outline: 'none',
              flex: 1,
              minWidth: '200px'
            }}
          />
          
          <input
            type="date"
            value={filters.dateTo}
            onChange={(e) => handleFilterChange('dateTo', e.target.value)}
            style={{
              padding: '12px 16px',
              border: 'none',
              borderRadius: '16px',
              background: '#F6F8FB',
              color: '#1F2937',
              fontSize: '14px',
              boxShadow: 'inset 4px 4px 8px #D1D9E6, inset -4px -4px 8px #FFFFFF',
              outline: 'none',
              flex: 1,
              minWidth: '200px'
            }}
          />
        </FiltersContainer>
        
        <TimelineContainer>
          <h3 style={{ marginBottom: '20px', color: '#1F2937', fontSize: '18px' }}>Prediction Timeline</h3>
          {filteredHistory.map((item, index) => (
            <TimelineItem key={item.id || index}>
              <TimelineDate>
                {item.created_at 
                  ? new Date(item.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric'
                    })
                  : 'N/A'}
              </TimelineDate>
              <TimelineContent>
                <TimelinePatient>
                  {item.patient?.full_name || 'Patient Name'}
                </TimelinePatient>
                <TimelineRisk risk={item.risk_score}>
                  Risk: {Math.round(item.risk_score * 100)}% ({item.risk_category})
                </TimelineRisk>
                <TimelineDoctor>
                  Dr. {item.doctor?.full_name || 'Doctor Name'}
                </TimelineDoctor>
                <ActionButtons>
                  <Button variant="primary" onClick={() => downloadPDF(item.id)}>
                    Download PDF
                  </Button>
                  <Button variant="secondary" onClick={() => deleteRecord(item.id)}>
                    Delete
                  </Button>
                </ActionButtons>
              </TimelineContent>
            </TimelineItem>
          ))}
        </TimelineContainer>
        
        {trends && trends.length > 0 && (
        <ChartsContainer>
          <ChartCard>
            <ChartTitle>Risk Score Trend</ChartTitle>
            <Line data={riskTrendData} options={chartOptions} />
          </ChartCard>
          
          <ChartCard>
            <ChartTitle>Glucose Level Trend</ChartTitle>
            <Line data={glucoseTrendData} options={chartOptions} />
          </ChartCard>
        </ChartsContainer>
        )}
      </ContentWrapper>
    </HistoryContainer>
  );
};

export default HistoryPage;