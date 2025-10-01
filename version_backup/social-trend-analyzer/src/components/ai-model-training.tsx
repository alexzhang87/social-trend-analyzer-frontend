import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Progress } from '@/components/ui/progress';
import { Slider } from '@/components/ui/slider';
import { 
  Brain, 
  Database, 
  Zap, 
  Settings, 
  Play, 
  Pause, 
  Square, 
  Download, 
  Upload,
  BarChart3,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  Cpu,
  HardDrive,
  Activity
} from 'lucide-react';

interface TrainingJob {
  id: string;
  name: string;
  model_type: 'glm4.5' | 'custom';
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused';
  progress: number;
  dataset_size: number;
  epochs: number;
  current_epoch: number;
  learning_rate: number;
  batch_size: number;
  loss: number;
  accuracy: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  estimated_time?: string;
  gpu_usage: number;
  memory_usage: number;
  specialization: 'pmf_analysis' | 'competitor_analysis' | 'market_trends' | 'business_insights';
}

interface ModelMetrics {
  training_loss: number[];
  validation_loss: number[];
  accuracy: number[];
  f1_score: number;
  precision: number;
  recall: number;
  inference_speed: number; // ms per request
  model_size: number; // MB
}

interface DatasetInfo {
  id: string;
  name: string;
  description: string;
  size: number;
  samples: number;
  categories: string[];
  quality_score: number;
  last_updated: string;
  source: 'internal' | 'external' | 'synthetic';
}

interface AIModelTrainingProps {
  onModelTrained?: (job: TrainingJob) => void;
}

const SPECIALIZATION_LABELS = {
  pmf_analysis: 'PMF Analysis Expert',
  competitor_analysis: 'Competitor Analysis Expert',
  market_trends: 'Market Trends Expert',
  business_insights: 'Business Insights Expert'
};

const STATUS_COLORS = {
  pending: 'bg-yellow-500',
  running: 'bg-blue-500',
  completed: 'bg-green-500',
  failed: 'bg-red-500',
  paused: 'bg-gray-500'
};

const STATUS_LABELS = {
  pending: 'Pending',
  running: 'Training',
  completed: 'Completed',
  failed: 'Failed',
  paused: 'Paused'
};

export function AIModelTraining({ onModelTrained }: AIModelTrainingProps) {
  const [trainingJobs, setTrainingJobs] = useState<TrainingJob[]>([]);
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  const [selectedJob, setSelectedJob] = useState<TrainingJob | null>(null);
  const [isCreatingJob, setIsCreatingJob] = useState(false);
  const [newJob, setNewJob] = useState({
    name: '',
    specialization: 'pmf_analysis' as const,
    dataset_id: '',
    epochs: 10,
    learning_rate: 0.001,
    batch_size: 32,
    model_type: 'glm4.5' as const
  });
  const [modelMetrics, setModelMetrics] = useState<ModelMetrics | null>(null);

  // Mock training task data
  useEffect(() => {
    const mockJobs: TrainingJob[] = [
      {
        id: '1',
        name: 'PMF Analysis Expert Model v2.1',
        model_type: 'glm4.5',
        status: 'running',
        progress: 65,
        dataset_size: 50000,
        epochs: 20,
        current_epoch: 13,
        learning_rate: 0.001,
        batch_size: 32,
        loss: 0.234,
        accuracy: 0.892,
        created_at: '2024-01-15',
        started_at: '2024-01-15 10:30',
        estimated_time: '2 hours 15 minutes',
        gpu_usage: 85,
        memory_usage: 12.5,
        specialization: 'pmf_analysis'
      },
      {
        id: '2',
        name: 'Competitor Threat Detection Model',
        model_type: 'glm4.5',
        status: 'completed',
        progress: 100,
        dataset_size: 75000,
        epochs: 15,
        current_epoch: 15,
        learning_rate: 0.0005,
        batch_size: 64,
        loss: 0.156,
        accuracy: 0.934,
        created_at: '2024-01-14',
        started_at: '2024-01-14 14:20',
        completed_at: '2024-01-14 18:45',
        gpu_usage: 0,
        memory_usage: 0,
        specialization: 'competitor_analysis'
      },
      {
        id: '3',
        name: 'Market Trend Prediction Model',
        model_type: 'glm4.5',
        status: 'pending',
        progress: 0,
        dataset_size: 120000,
        epochs: 25,
        current_epoch: 0,
        learning_rate: 0.002,
        batch_size: 16,
        loss: 0,
        accuracy: 0,
        created_at: '2024-01-15',
        gpu_usage: 0,
        memory_usage: 0,
        specialization: 'market_trends'
      }
    ];
    setTrainingJobs(mockJobs);

    const mockDatasets: DatasetInfo[] = [
      {
        id: 'ds1',
        name: 'PMF Assessment Dataset',
        description: 'Historical data and user feedback for product-market fit assessment',
        size: 2.5, // GB
        samples: 50000,
        categories: ['User Feedback', 'Market Research', 'NPS Scores', 'Usage Behavior'],
        quality_score: 92,
        last_updated: '2024-01-10',
        source: 'internal'
      },
      {
        id: 'ds2',
        name: 'Competitor Analysis Dataset',
        description: 'Competitor product information, pricing strategies, and market performance data',
        size: 4.2,
        samples: 75000,
        categories: ['Product Features', 'Pricing Info', 'Market Share', 'User Reviews'],
        quality_score: 88,
        last_updated: '2024-01-12',
        source: 'external'
      },
      {
        id: 'ds3',
        name: 'Market Trends Dataset',
        description: 'Comprehensive data from social media trends, search popularity, and industry reports',
        size: 8.7,
        samples: 120000,
        categories: ['Social Media', 'Search Trends', 'Industry Reports', 'News & Information'],
        quality_score: 95,
        last_updated: '2024-01-14',
        source: 'synthetic'
      }
    ];
    setDatasets(mockDatasets);
  }, []);

  // Mock model metrics
  useEffect(() => {
    if (selectedJob && selectedJob.status === 'completed') {
      const mockMetrics: ModelMetrics = {
        training_loss: [0.8, 0.6, 0.4, 0.3, 0.25, 0.2, 0.18, 0.16],
        validation_loss: [0.85, 0.65, 0.45, 0.35, 0.28, 0.22, 0.19, 0.17],
        accuracy: [0.6, 0.72, 0.81, 0.86, 0.89, 0.91, 0.93, 0.934],
        f1_score: 0.928,
        precision: 0.941,
        recall: 0.915,
        inference_speed: 45,
        model_size: 1250
      };
      setModelMetrics(mockMetrics);
    } else {
      setModelMetrics(null);
    }
  }, [selectedJob]);

  // Create training task
  const createTrainingJob = async () => {
    if (!newJob.name || !newJob.dataset_id) return;
    
    const job: TrainingJob = {
      id: Date.now().toString(),
      name: newJob.name,
      model_type: newJob.model_type,
      status: 'pending',
      progress: 0,
      dataset_size: datasets.find(d => d.id === newJob.dataset_id)?.samples || 0,
      epochs: newJob.epochs,
      current_epoch: 0,
      learning_rate: newJob.learning_rate,
      batch_size: newJob.batch_size,
      loss: 0,
      accuracy: 0,
      created_at: new Date().toISOString().split('T')[0],
      gpu_usage: 0,
      memory_usage: 0,
      specialization: newJob.specialization
    };
    
    setTrainingJobs(prev => [...prev, job]);
    setIsCreatingJob(false);
    setNewJob({
      name: '',
      specialization: 'pmf_analysis',
      dataset_id: '',
      epochs: 10,
      learning_rate: 0.001,
      batch_size: 32,
      model_type: 'glm4.5'
    });
    
    if (onModelTrained) {
      onModelTrained(job);
    }
  };

  // Control training task
  const controlJob = (jobId: string, action: 'start' | 'pause' | 'stop') => {
    setTrainingJobs(prev => prev.map(job => {
      if (job.id === jobId) {
        switch (action) {
          case 'start':
            return { ...job, status: 'running' as const };
          case 'pause':
            return { ...job, status: 'paused' as const };
          case 'stop':
            return { ...job, status: 'failed' as const };
          default:
            return job;
        }
      }
      return job;
    }));
  };

  // Get resource usage statistics
  const getResourceStats = () => {
    const runningJobs = trainingJobs.filter(job => job.status === 'running');
    const totalGpuUsage = runningJobs.reduce((sum, job) => sum + job.gpu_usage, 0);
    const totalMemoryUsage = runningJobs.reduce((sum, job) => sum + job.memory_usage, 0);
    
    return {
      activeJobs: runningJobs.length,
      gpuUsage: Math.min(totalGpuUsage, 100),
      memoryUsage: totalMemoryUsage,
      completedJobs: trainingJobs.filter(job => job.status === 'completed').length
    };
  };

  const resourceStats = getResourceStats();

  return (
    <div className="space-y-6">
      {/* 资源监控概览 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active Training</p>
                <p className="text-2xl font-bold text-white">{resourceStats.activeJobs}</p>
              </div>
              <Activity className="w-8 h-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">GPU Usage</p>
                <p className="text-2xl font-bold text-green-400">{resourceStats.gpuUsage}%</p>
              </div>
              <Cpu className="w-8 h-8 text-green-400" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Memory Usage</p>
                <p className="text-2xl font-bold text-purple-400">{resourceStats.memoryUsage.toFixed(1)}GB</p>
              </div>
              <HardDrive className="w-8 h-8 text-purple-400" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Completed</p>
                <p className="text-2xl font-bold text-cyan-400">{resourceStats.completedJobs}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-cyan-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="jobs" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="jobs">Training Jobs</TabsTrigger>
          <TabsTrigger value="datasets">Datasets</TabsTrigger>
          <TabsTrigger value="metrics">Model Metrics</TabsTrigger>
          <TabsTrigger value="create">Create Job</TabsTrigger>
        </TabsList>
        
        {/* 训练任务 */}
        <TabsContent value="jobs" className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">AI Model Training Jobs</h3>
            <Button 
              onClick={() => setIsCreatingJob(true)}
              className="bg-cyan-600 hover:bg-cyan-700"
            >
              <Brain className="w-4 h-4 mr-2" />
              New Training
            </Button>
          </div>
          
          <div className="grid grid-cols-1 gap-4">
            {trainingJobs.map(job => (
              <Card 
                key={job.id} 
                className={`border-border/20 bg-card/50 backdrop-blur-sm cursor-pointer transition-colors ${
                  selectedJob?.id === job.id ? 'ring-2 ring-cyan-400' : 'hover:bg-card/70'
                }`}
                onClick={() => setSelectedJob(job)}
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{job.name}</CardTitle>
                      <CardDescription>
                        {SPECIALIZATION_LABELS[job.specialization]} • {job.model_type.toUpperCase()}
                      </CardDescription>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={`${STATUS_COLORS[job.status]} text-white`}>
                        {STATUS_LABELS[job.status]}
                      </Badge>
                      {job.status === 'running' && (
                        <div className="flex gap-1">
                          <Button size="sm" variant="outline" onClick={(e) => {
                            e.stopPropagation();
                            controlJob(job.id, 'pause');
                          }}>
                            <Pause className="w-3 h-3" />
                          </Button>
                          <Button size="sm" variant="outline" onClick={(e) => {
                            e.stopPropagation();
                            controlJob(job.id, 'stop');
                          }}>
                            <Square className="w-3 h-3" />
                          </Button>
                        </div>
                      )}
                      {job.status === 'paused' && (
                        <Button size="sm" variant="outline" onClick={(e) => {
                          e.stopPropagation();
                          controlJob(job.id, 'start');
                        }}>
                          <Play className="w-3 h-3" />
                        </Button>
                      )}
                      {job.status === 'pending' && (
                        <Button size="sm" variant="outline" onClick={(e) => {
                          e.stopPropagation();
                          controlJob(job.id, 'start');
                        }}>
                          <Play className="w-3 h-3" />
                        </Button>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {job.status === 'running' && (
                      <div>
                        <div className="flex justify-between text-sm mb-2">
                          <span>Training Progress</span>
                          <span>{job.current_epoch}/{job.epochs} epochs ({job.progress}%)</span>
                        </div>
                        <Progress value={job.progress} className="mb-2" />
                        {job.estimated_time && (
                          <p className="text-xs text-muted-foreground">Estimated Time Remaining: {job.estimated_time}</p>
                        )}
                      </div>
                    )}
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Dataset Size</p>
                        <p className="font-medium">{job.dataset_size.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Learning Rate</p>
                        <p className="font-medium">{job.learning_rate}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Batch Size</p>
                        <p className="font-medium">{job.batch_size}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Current Loss</p>
                        <p className="font-medium">{job.loss.toFixed(3)}</p>
                      </div>
                    </div>
                    
                    {job.status === 'running' && (
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-muted-foreground">GPU Usage</p>
                          <div className="flex items-center gap-2">
                            <Progress value={job.gpu_usage} className="flex-1" />
                            <span className="text-xs">{job.gpu_usage}%</span>
                          </div>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Memory Usage</p>
                          <p className="font-medium">{job.memory_usage.toFixed(1)}GB</p>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
        
        {/* 数据集管理 */}
        <TabsContent value="datasets" className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Training Datasets</h3>
            <Button className="bg-green-600 hover:bg-green-700">
              <Upload className="w-4 h-4 mr-2" />
              Upload Dataset
            </Button>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {datasets.map(dataset => (
              <Card key={dataset.id} className="border-border/20 bg-card/50 backdrop-blur-sm">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg">{dataset.name}</CardTitle>
                      <CardDescription>{dataset.description}</CardDescription>
                    </div>
                    <Badge className={`${
                      dataset.source === 'internal' ? 'bg-blue-500' :
                      dataset.source === 'external' ? 'bg-green-500' : 'bg-purple-500'
                    } text-white`}>
                      {dataset.source === 'internal' ? 'Internal' :
                       dataset.source === 'external' ? 'External' : 'Synthetic'}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Sample Count</p>
                        <p className="font-medium">{dataset.samples.toLocaleString()} samples</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">File Size</p>
                        <p className="font-medium">{dataset.size}GB</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Quality Score</p>
                        <div className="flex items-center gap-2">
                          <Progress value={dataset.quality_score} className="flex-1" />
                          <span className="text-xs">{dataset.quality_score}%</span>
                        </div>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Last Updated</p>
                        <p className="font-medium">{dataset.last_updated}</p>
                      </div>
                    </div>
                    
                    <div>
                      <p className="text-sm text-muted-foreground mb-2">Data Categories:</p>
                      <div className="flex flex-wrap gap-1">
                        {dataset.categories.map(category => (
                          <Badge key={category} variant="outline" className="text-xs">
                            {category}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline">
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </Button>
                      <Button size="sm" variant="outline">
                        <BarChart3 className="w-4 h-4 mr-2" />
                        Analyze
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
        
        {/* 模型指标 */}
        <TabsContent value="metrics" className="space-y-4">
          {selectedJob ? (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Model Performance Metrics</h3>
                <Badge className={`${STATUS_COLORS[selectedJob.status]} text-white`}>
                  {selectedJob.name}
                </Badge>
              </div>
              
              {modelMetrics ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle>Training Metrics</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center">
                          <p className="text-2xl font-bold text-green-400">{(modelMetrics.accuracy[modelMetrics.accuracy.length - 1] * 100).toFixed(1)}%</p>
                          <p className="text-sm text-muted-foreground">Accuracy</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-blue-400">{modelMetrics.f1_score.toFixed(3)}</p>
                          <p className="text-sm text-muted-foreground">F1 Score</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-purple-400">{modelMetrics.precision.toFixed(3)}</p>
                          <p className="text-sm text-muted-foreground">Precision</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-cyan-400">{modelMetrics.recall.toFixed(3)}</p>
                          <p className="text-sm text-muted-foreground">Recall</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle>Performance Metrics</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Inference Speed</span>
                          <span className="font-medium">{modelMetrics.inference_speed}ms</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Model Size</span>
                          <span className="font-medium">{modelMetrics.model_size}MB</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Training Loss</span>
                          <span className="font-medium">{modelMetrics.training_loss[modelMetrics.training_loss.length - 1].toFixed(3)}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Validation Loss</span>
                          <span className="font-medium">{modelMetrics.validation_loss[modelMetrics.validation_loss.length - 1].toFixed(3)}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card className="lg:col-span-2 border-border/20 bg-card/50 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle>Training Curves</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-64 flex items-center justify-center text-muted-foreground">
                        <div className="text-center">
                          <TrendingUp className="w-12 h-12 mx-auto mb-2 opacity-50" />
                          <p>Training Curve Charts</p>
                          <p className="text-xs">Integrate Chart.js or other charting libraries to display training progress</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ) : (
                <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
                  <CardContent className="p-8 text-center">
                    <AlertCircle className="w-16 h-16 mx-auto mb-4 text-yellow-400 opacity-50" />
                    <h3 className="text-lg font-semibold mb-2">Model Training Not Completed</h3>
                    <p className="text-muted-foreground">Detailed performance metrics will be displayed after training completion</p>
                  </CardContent>
                </Card>
              )}
            </div>
          ) : (
            <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
              <CardContent className="p-8 text-center">
                <Brain className="w-16 h-16 mx-auto mb-4 text-cyan-400 opacity-50" />
                <h3 className="text-lg font-semibold mb-2">Select Training Job</h3>
                <p className="text-muted-foreground">Select a training job from the left to view detailed metrics</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
        
        {/* 创建训练任务 */}
        <TabsContent value="create" className="space-y-4">
          <Card className="border-border/20 bg-card/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle>Create New Training Job</CardTitle>
              <CardDescription>Configure specialized training parameters for GLM4.5 model</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="job-name">Job Name</Label>
                  <Input
                    id="job-name"
                    value={newJob.name}
                    onChange={(e) => setNewJob(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Enter training job name"
                  />
                </div>
                <div>
                  <Label htmlFor="specialization">Specialization</Label>
                  <Select 
                    value={newJob.specialization} 
                    onValueChange={(value: any) => setNewJob(prev => ({ ...prev, specialization: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pmf_analysis">PMF Analysis Expert</SelectItem>
                      <SelectItem value="competitor_analysis">Competitor Analysis Expert</SelectItem>
                      <SelectItem value="market_trends">Market Trends Expert</SelectItem>
                      <SelectItem value="business_insights">Business Insights Expert</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="dataset">Training Dataset</Label>
                  <Select 
                    value={newJob.dataset_id} 
                    onValueChange={(value) => setNewJob(prev => ({ ...prev, dataset_id: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select dataset" />
                    </SelectTrigger>
                    <SelectContent>
                      {datasets.map(dataset => (
                        <SelectItem key={dataset.id} value={dataset.id}>
                          {dataset.name} ({dataset.samples.toLocaleString()} samples)
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="model-type">Model Type</Label>
                  <Select 
                    value={newJob.model_type} 
                    onValueChange={(value: any) => setNewJob(prev => ({ ...prev, model_type: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="glm4.5">GLM-4.5</SelectItem>
                      <SelectItem value="custom">Custom Model</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="epochs">Training Epochs: {newJob.epochs}</Label>
                  <Slider
                    id="epochs"
                    min={5}
                    max={50}
                    step={5}
                    value={[newJob.epochs]}
                    onValueChange={([value]) => setNewJob(prev => ({ ...prev, epochs: value }))}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="learning-rate">Learning Rate: {newJob.learning_rate}</Label>
                  <Slider
                    id="learning-rate"
                    min={0.0001}
                    max={0.01}
                    step={0.0001}
                    value={[newJob.learning_rate]}
                    onValueChange={([value]) => setNewJob(prev => ({ ...prev, learning_rate: value }))}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="batch-size">Batch Size: {newJob.batch_size}</Label>
                  <Slider
                    id="batch-size"
                    min={8}
                    max={128}
                    step={8}
                    value={[newJob.batch_size]}
                    onValueChange={([value]) => setNewJob(prev => ({ ...prev, batch_size: value }))}
                    className="mt-2"
                  />
                </div>
              </div>
              
              <div className="flex gap-2">
                <Button 
                  onClick={createTrainingJob}
                  className="bg-green-600 hover:bg-green-700"
                  disabled={!newJob.name || !newJob.dataset_id}
                >
                  <Zap className="w-4 h-4 mr-2" />
                  Start Training
                </Button>
                <Button variant="outline">
                  <Settings className="w-4 h-4 mr-2" />
                  Advanced Settings
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}