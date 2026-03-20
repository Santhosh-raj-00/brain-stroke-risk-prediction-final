import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
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
  Title,
  Tooltip,
  Legend
);

const PatientsContainer = styled.div`
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

const TableContainer = styled.div`
  background: #F6F8FB;
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 40px;
  box-shadow:
    8px 8px 18px #D1D9E6,
    -8px -8px 18px #FFFFFF;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  
  th, td {
    padding: 16px;
    text-align: left;
    border-bottom: 1px solid #E5E7EB;
  }
  
  th {
    color: #6B7280;
    font-weight: 500;
    font-size: 14px;
  }
  
  tr:last-child td {
    border-bottom: none;
  }
`;

const RiskBadge = styled.span`
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background-color: ${props => {
    if (props.level === 'LOW') return 'rgba(34, 197, 94, 0.1)';
    if (props.level === 'MEDIUM') return 'rgba(245, 158, 11, 0.1)';
    return 'rgba(239, 68, 68, 0.1)';
  }};
  color: ${props => {
    if (props.level === 'LOW') return '#22C55E';
    if (props.level === 'MEDIUM') return '#F59E0B';
    return '#EF4444';
  }};
`;

const ChartsContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
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

const ActionButton = styled.button`
  background: #6C7CFF;
  color: white;
  border: none;
  border-radius: 16px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  box-shadow:
    4px 4px 10px rgba(108, 124, 255, 0.2),
    -4px -4px 10px rgba(255, 255, 255, 0.6);
  transition: all 0.3s ease;

  &:hover {
    background: #5a6ae6;
    box-shadow:
      2px 2px 6px rgba(108, 124, 255, 0.2),
      -2px -2px 6px rgba(255, 255, 255, 0.6);
  }
`;

const PatientsPage = () => {
  const [patients, setPatients] = useState([]);
  const [filteredPatients, setFilteredPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [filters, setFilters] = useState({
    risk: '',
    dateFrom: '',
    dateTo: '',
    ageGroup: ''
  });
  
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        // Use relative path for proxy configuration
        const apiUrl = process.env.REACT_APP_API_URL;
        let url = apiUrl && apiUrl !== '/' ? `${apiUrl}/api/patients` : '/api/patients';
        
        // Add query parameters properly
        const params = new URLSearchParams();
        if (filters.risk) {
          params.append('risk_level', filters.risk);
        }
        
        if (params.toString()) {
          url += `?${params.toString()}`;
        }
        
        console.log('Fetching patients with URL:', url); // Debug log
        
        const response = await axios.get(
          url,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
          }
        );
        
        console.log('Patients response:', response.data); // Debug log
        setPatients(response.data);
        setFilteredPatients(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load patients');
        setLoading(false);
        console.error('Error fetching patients:', err);
      }
    };

    fetchPatients();
  }, [filters.risk]); // Only refetch when risk filter changes

  // Apply filters (excluding risk level which is handled by backend)
  useEffect(() => {
    let result = [...patients];
    
    if (filters.dateFrom) {
      result = result.filter(patient => 
        patient.last_prediction_date && patient.last_prediction_date >= filters.dateFrom
      );
    }
    
    if (filters.dateTo) {
      result = result.filter(patient => 
        patient.last_prediction_date && patient.last_prediction_date <= filters.dateTo
      );
    }
    
    if (filters.ageGroup) {
      result = result.filter(patient => {
        const age = patient.age;
        if (filters.ageGroup === '0-30') return age >= 0 && age <= 30;
        if (filters.ageGroup === '31-50') return age >= 31 && age <= 50;
        if (filters.ageGroup === '51-70') return age >= 51 && age <= 70;
        return age > 70;
      });
    }
    
    setFilteredPatients(result);
  }, [filters, patients]);

  const handleFilterChange = (filterName, value) => {
    console.log('Filter changed:', filterName, '=', value); // Debug log
    setFilters(prev => {
      const newFilters = {
        ...prev,
        [filterName]: value
      };
      console.log('New filters:', newFilters); // Debug log
      return newFilters;
    });
  };

  // Prepare chart data
  const riskDistributionData = {
    labels: ['Low Risk', 'Medium Risk', 'High Risk'],
    datasets: [
      {
        data: [
          filteredPatients.filter(p => p.last_risk_category === 'LOW').length,
          filteredPatients.filter(p => p.last_risk_category === 'MEDIUM').length,
          filteredPatients.filter(p => p.last_risk_category === 'HIGH').length
        ],
        backgroundColor: ['#22C55E', '#F59E0B', '#EF4444'],
        borderColor: ['#16A34A', '#D97706', '#DC2626'],
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
          filteredPatients.filter(p => p.age >= 0 && p.age <= 30).length,
          filteredPatients.filter(p => p.age >= 31 && p.age <= 50).length,
          filteredPatients.filter(p => p.age >= 51 && p.age <= 70).length,
          filteredPatients.filter(p => p.age > 70).length
        ],
        backgroundColor: ['#6C7CFF', '#A78BFA', '#38BDF8', '#F59E0B'],
        borderColor: ['#4F46E5', '#8B5CF6', '#0EA5E9', '#D97706'],
        borderWidth: 1,
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
            return `${context.label}: ${context.parsed}`;
          }
        }
      }
    }
  };

  if (loading) {
    return (
      <PatientsContainer>
        <ContentWrapper>
          <div className="flex-center">Loading patients...</div>
        </ContentWrapper>
      </PatientsContainer>
    );
  }

  if (error) {
    return (
      <PatientsContainer>
        <ContentWrapper>
          <div className="flex-center">{error}</div>
        </ContentWrapper>
      </PatientsContainer>
    );
  }

  return (
    <PatientsContainer>
      <ContentWrapper>
        <Header>
          <PageTitle>Patients Management</PageTitle>
          <Subtitle>Manage patient records and view prediction history</Subtitle>
        </Header>
        
        <FiltersContainer>
          <FilterSelect 
            value={filters.risk} 
            onChange={(e) => handleFilterChange('risk', e.target.value)}
          >
            <option value="">All Risk Levels</option>
            <option value="LOW">Low Risk</option>
            <option value="MEDIUM">Medium Risk</option>
            <option value="HIGH">High Risk</option>
          </FilterSelect>
          
          <FilterSelect 
            value={filters.ageGroup} 
            onChange={(e) => handleFilterChange('ageGroup', e.target.value)}
          >
            <option value="">All Age Groups</option>
            <option value="0-30">0-30 Years</option>
            <option value="31-50">31-50 Years</option>
            <option value="51-70">51-70 Years</option>
            <option value="71+">71+ Years</option>
          </FilterSelect>
          
          <ActionButton onClick={() => navigate('/prediction')}>
            Add New Patient
          </ActionButton>
        </FiltersContainer>
        
        <TableContainer>
          <Table>
            <thead>
              <tr>
                <th>Patient Name</th>
                <th>Age</th>
                <th>Last Risk %</th>
                <th>Risk Level</th>
                <th>Last Prediction</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredPatients.map((patient, index) => (
                <tr key={patient.id || index}>
                  <td>{patient.full_name}</td>
                  <td>{patient.age}</td>
                  <td>
                    {patient.last_risk_score !== null 
                      ? `${Math.round(patient.last_risk_score * 100)}%` 
                      : 'No predictions yet'}
                  </td>
                  <td>
                    {patient.last_risk_score !== null ? (
                      <RiskBadge level={patient.last_risk_category}>
                        {patient.last_risk_category}
                      </RiskBadge>
                    ) : (
                      'No predictions yet'
                    )}
                  </td>
                  <td>
                    {patient.last_prediction_date 
                      ? new Date(patient.last_prediction_date).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric'
                        })
                      : 'No predictions yet'}
                  </td>
                  <td>
                    <ActionButton onClick={() => navigate(`/history?patient_id=${patient.id}`)}>
                      View
                    </ActionButton>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </TableContainer>
        
        <ChartsContainer>
          <ChartCard>
            <ChartTitle>Risk Distribution</ChartTitle>
            <Pie data={riskDistributionData} options={chartOptions} />
          </ChartCard>
          
          <ChartCard>
            <ChartTitle>Age Distribution</ChartTitle>
            <Bar data={ageDistributionData} options={chartOptions} />
          </ChartCard>
        </ChartsContainer>
      </ContentWrapper>
    </PatientsContainer>
  );
};

export default PatientsPage;