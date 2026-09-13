// ============================================================
// CommitIQ — Core TypeScript Types
// ============================================================

export type Theme = 'dark' | 'light';

export type CommitCategory =
  | 'FEATURE'
  | 'BUG_FIX'
  | 'REFACTORING'
  | 'TESTING'
  | 'DOCUMENTATION'
  | 'CONFIGURATION'
  | 'PERFORMANCE'
  | 'SECURITY'
  | 'OTHER';

export type QualityLevel = 'excellent' | 'good' | 'moderate' | 'poor';

export interface QualityBreakdown {
  clarity: number;
  specificity: number;
  actionability: number;
  context: number;
  consistency: number;
}

export interface CommitIssue {
  type: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
}

export interface FileChange {
  filename: string;
  additions: number;
  deletions: number;
  status: 'added' | 'modified' | 'deleted' | 'renamed';
}

export interface CommitAnalysis {
  commitHash: string;
  repositoryId: string;
  author: string;
  authorAvatar?: string;
  message: string;
  timestamp: string;
  branch: string;
  changedFiles: FileChange[];
  filesChanged: number;
  additions: number;
  deletions: number;
  category: CommitCategory;
  confidence: number;
  qualityScore: number;
  qualityLevel: QualityLevel;
  qualityBreakdown: QualityBreakdown;
  detectedIssues: CommitIssue[];
  suggestedMessage: string;
  messageChangeConsistency: {
    isConsistent: boolean;
    mismatchReason?: string;
    confidence: number;
  };
  createdAt: string;
  updatedAt: string;
}

export interface Repository {
  id: string;
  name: string;
  fullName: string;
  owner: string;
  ownerAvatar?: string;
  description?: string;
  visibility: 'public' | 'private';
  defaultBranch: string;
  stars: number;
  forks: number;
  language?: string;
  lastActivity: string;
  totalCommits?: number;
  analyzedCommits?: number;
  analysisStatus: 'pending' | 'analyzing' | 'completed' | 'failed' | 'not_started';
  healthScore?: number;
  averageQuality?: number;
  createdAt: string;
  updatedAt: string;
}

export interface Contributor {
  id: string;
  login: string;
  name?: string;
  avatar: string;
  totalCommits: number;
  averageQuality: number;
  mostCommonCategory: CommitCategory;
  poorCommitPercentage: number;
  commitsByCategory: Record<CommitCategory, number>;
  recentActivity: { date: string; count: number }[];
  firstCommit: string;
  lastCommit: string;
}

export interface RepositoryAnalytics {
  repositoryId: string;
  totalCommits: number;
  analyzedCommits: number;
  averageQuality: number;
  poorCommits: number;
  excellentCommits: number;
  commitsByCategory: Record<CommitCategory, number>;
  commitsByDay: { date: string; count: number }[];
  qualityOverTime: { date: string; score: number }[];
  categoryOverTime: { date: string; categories: Partial<Record<CommitCategory, number>> }[];
  topContributors: string[];
  trends: Trend[];
  healthScore: number;
  healthFactors: HealthFactor[];
}

export interface Trend {
  type: 'increasing' | 'decreasing' | 'stable';
  metric: string;
  description: string;
  percentChange: number;
  direction: 'positive' | 'negative' | 'neutral';
}

export interface HealthFactor {
  name: string;
  score: number;
  weight: number;
  description: string;
}

export interface Recommendation {
  id: string;
  repositoryId: string;
  commitHash?: string;
  type: 'poor_message' | 'mismatch' | 'trend' | 'quality_improvement';
  title: string;
  description: string;
  originalMessage?: string;
  suggestedMessage?: string;
  priority: 'high' | 'medium' | 'low';
  createdAt: string;
}

export interface ActivityEvent {
  id: string;
  type: 'commit_analyzed' | 'repository_connected' | 'analysis_completed' | 'poor_commit_detected' | 'recommendation_generated' | 'quality_improved' | 'webhook_received';
  title: string;
  description: string;
  repositoryId?: string;
  repositoryName?: string;
  commitHash?: string;
  metadata?: Record<string, unknown>;
  timestamp: string;
}

export interface User {
  id: string;
  login: string;
  name?: string;
  email?: string;
  avatar: string;
  githubConnected: boolean;
  createdAt: string;
}

export interface SearchResult {
  commits: CommitAnalysis[];
  repositories: Repository[];
  contributors: Contributor[];
  files: { path: string; repositoryId: string; repositoryName: string }[];
}

export interface ModelMetrics {
  accuracy: number;
  precision: Record<CommitCategory, number>;
  recall: Record<CommitCategory, number>;
  f1Score: Record<CommitCategory, number>;
  macroF1: number;
  confusionMatrix: number[][];
  classes: CommitCategory[];
  trainedAt: string;
  datasetSize: number;
  trainSize: number;
  testSize: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface ApiError {
  message: string;
  code?: string;
  statusCode?: number;
}

export type DateRange = '7d' | '30d' | '90d' | '6m' | '1y' | 'all' | 'custom';

export interface FilterState {
  search: string;
  category: CommitCategory | 'all';
  qualityLevel: QualityLevel | 'all';
  author: string;
  dateRange: DateRange;
  sortBy: 'date' | 'quality' | 'category';
  sortOrder: 'asc' | 'desc';
  page: number;
  limit: number;
}
