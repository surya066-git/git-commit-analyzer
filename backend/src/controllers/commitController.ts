import { Request, Response } from 'express';
import { analyzeCommit, AnalysisRequest } from '../services/mlService';

export const analyzeCommitHandler = async (req: Request, res: Response) => {
    try {
        const { commitMessage, changedFiles, additions, deletions } = req.body;

        if (!commitMessage || typeof commitMessage !== 'string' || commitMessage.trim() === '') {
            return res.status(400).json({ error: 'commitMessage is required and must be a non-empty string' });
        }

        const requestPayload: AnalysisRequest = {
            commitMessage,
            changedFiles: Array.isArray(changedFiles) ? changedFiles : [],
            additions: typeof additions === 'number' ? additions : 0,
            deletions: typeof deletions === 'number' ? deletions : 0
        };

        const analysisResult = await analyzeCommit(requestPayload);
        
        res.status(200).json(analysisResult);
    } catch (error: any) {
        console.error('Error analyzing commit:', error.message);
        res.status(503).json({ error: error.message || 'Analysis service is currently unavailable.' });
    }
};
