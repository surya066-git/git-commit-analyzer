import axios from 'axios';

const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:8000';

export interface AnalysisRequest {
    commitMessage: string;
    changedFiles?: string[];
    additions?: number;
    deletions?: number;
}

export const analyzeCommit = async (request: AnalysisRequest) => {
    try {
        const response = await axios.post(`${ML_SERVICE_URL}/api/analyze`, request, {
            timeout: 5000 // 5 seconds timeout
        });
        return response.data;
    } catch (error: any) {
        if (error.code === 'ECONNABORTED') {
            throw new Error('Analysis service is currently unavailable (timeout).');
        }
        if (!error.response) {
            throw new Error('Analysis service is currently unavailable.');
        }
        throw new Error(error.response?.data?.detail || 'Failed to analyze commit');
    }
};
