import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

const HomeContainer = styled.div`
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

const Title = styled.h1`
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

const MainCard = styled.div`
  background: #F6F8FB;
  border-radius: 20px;
  padding: 40px;
  margin-bottom: 40px;
  box-shadow:
    8px 8px 18px #D1D9E6,
    -8px -8px 18px #FFFFFF;
`;

const SectionTitle = styled.h2`
  color: #1F2937;
  font-size: 24px;
  margin-bottom: 24px;
  text-align: center;
`;

const HowItWorksGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
`;

const WorkStep = styled.div`
  background: #F6F8FB;
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  box-shadow:
    inset 4px 4px 8px #D1D9E6,
    inset -4px -4px 8px #FFFFFF;
`;

const StepNumber = styled.div`
  width: 40px;
  height: 40px;
  background: #6C7CFF;
  color: white;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto 16px;
  font-weight: bold;
`;

const StepTitle = styled.h3`
  color: #1F2937;
  margin-bottom: 12px;
  font-size: 16px;
`;

const StepDescription = styled.p`
  color: #6B7280;
  font-size: 14px;
  line-height: 1.5;
`;

const DatasetInfo = styled.div`
  background: #F6F8FB;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 40px;
  box-shadow:
    inset 4px 4px 8px #D1D9E6,
    inset -4px -4px 8px #FFFFFF;
`;

const DatasetTitle = styled.h3`
  color: #1F2937;
  margin-bottom: 16px;
  font-size: 18px;
`;

const DatasetDescription = styled.p`
  color: #6B7280;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 16px;
`;

const DatasetList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
  
  li {
    color: #6B7280;
    font-size: 14px;
    margin-bottom: 8px;
    position: relative;
    padding-left: 20px;
    
    &:before {
      content: '•';
      color: #6C7CFF;
      position: absolute;
      left: 0;
    }
  }
`;

const StartButton = styled(Link)`
  display: block;
  width: 250px;
  margin: 0 auto;
  background: #6C7CFF;
  color: white;
  border: none;
  border-radius: 16px;
  padding: 16px 32px;
  font-size: 16px;
  font-weight: 500;
  text-decoration: none;
  text-align: center;
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

const HomePage = () => {
  return (
    <HomeContainer>
      <ContentWrapper>
        <Header>
          <Title>Brain Stroke Risk Prediction System</Title>
          <Subtitle>Advanced ML-powered clinical decision support for stroke risk assessment</Subtitle>
        </Header>
        
        <MainCard>
          <SectionTitle>How Stroke Prediction Works</SectionTitle>
          
          <HowItWorksGrid>
            <WorkStep>
              <StepNumber>1</StepNumber>
              <StepTitle>Data Input</StepTitle>
              <StepDescription>
                Enter patient demographics and medical history including age, gender, 
                hypertension, heart disease, glucose levels, and BMI.
              </StepDescription>
            </WorkStep>
            
            <WorkStep>
              <StepNumber>2</StepNumber>
              <StepTitle>ML Risk Prediction</StepTitle>
              <StepDescription>
                Our XGBoost model analyzes input data to predict stroke risk 
                probability using proven algorithms.
              </StepDescription>
            </WorkStep>
            
            <WorkStep>
              <StepNumber>3</StepNumber>
              <StepTitle>MRI/CT Analysis</StepTitle>
              <StepDescription>
                Upload medical imaging for automated analysis and validation 
                using deep learning techniques.
              </StepDescription>
            </WorkStep>
            
            <WorkStep>
              <StepNumber>4</StepNumber>
              <StepTitle>Explainable Results</StepTitle>
              <StepDescription>
                View SHAP-based explanations showing which factors contributed 
                most to the risk prediction.
              </StepDescription>
            </WorkStep>
          </HowItWorksGrid>
          
          <DatasetInfo>
            <DatasetTitle>Training Dataset: Kaggle Stroke Prediction Dataset</DatasetTitle>
            <DatasetDescription>
              Our ML models are trained on a comprehensive dataset of stroke cases with verified outcomes, 
              ensuring reliable and accurate predictions.
            </DatasetDescription>
            <DatasetList>
              <li>Demographic data (age, gender, residence type)</li>
              <li>Medical history (hypertension, heart disease)</li>
              <li>Lifestyle factors (smoking, work type)</li>
              <li>Clinical measurements (glucose, BMI)</li>
              <li>Imaging validation (MRI/CT modality detection)</li>
            </DatasetList>
          </DatasetInfo>
          
          <StartButton to="/prediction">
            Start New Prediction
          </StartButton>
        </MainCard>
      </ContentWrapper>
    </HomeContainer>
  );
};

export default HomePage;