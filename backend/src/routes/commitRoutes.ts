import { Router } from 'express';
import { analyzeCommitHandler } from '../controllers/commitController';

const router = Router();

router.post('/analyze', analyzeCommitHandler);

export default router;
