import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { ScrollArea } from './ui/scroll-area';
import { Separator } from './ui/separator';
import { Alert, AlertDescription } from './ui/alert';
import { Loader2, Search, Twitter, MessageSquare, ExternalLink, Calendar, User, Heart, MessageCircle, Repeat2 } from 'lucide-react';
import { XLogo } from './ui/x-logo';
import { RedditLogo } from './ui/reddit-logo';

interface TwitterPost {
  id: string;
  content: string;
  date: string;
  user: {
    username: string;
    displayname: string;
    followers_count: number;
  };
  metrics: {
    retweet_count: number;
    like_count: number;
    reply_count: number;
  };
  url: string;
}

interface RedditPost {
  id: string;
  title: string;
  content: string;
  url: string;
  permalink: string;
  subreddit: string;
  author: string;
  created_utc: string;
  metrics: {
    score: number;
    upvote_ratio: number;
    num_comments: number;
  };
  flair?: string;
  is_nsfw: boolean;
}

interface SocialScrapingPanelProps {
  className?: string;
}

const SocialScrapingPanel: React.FC<SocialScrapingPanelProps> = ({ className }) => {
  const [activeTab, setActiveTab] = useState('twitter');
  const [searchQuery, setSearchQuery] = useState('');
  const [username, setUsername] = useState('');
  const [subreddit, setSubreddit] = useState('');
  const [loading, setLoading] = useState(false);
  const [twitterPosts, setTwitterPosts] = useState<TwitterPost[]>([]);
  const [redditPosts, setRedditPosts] = useState<RedditPost[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<{twitter: boolean, reddit: boolean} | null>(null);

  const API_BASE_URL = process.env.NODE_ENV === 'production' 
    ? 'https://your-production-api.com' 
    : 'http://localhost:8000';

  // Check connection status
  useEffect(() => {
    checkConnectionStatus();
  }, []);

  const checkConnectionStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/social-scraping/status`);
      if (response.ok) {
        const data = await response.json();
        setConnectionStatus(data.platforms);
      }
    } catch (error) {
      console.error('Failed to check connection status:', error);
    }
  };

  const searchTwitter = async () => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/social-scraping/twitter/search?query=${encodeURIComponent(searchQuery)}&limit=20`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setTwitterPosts(data.tweets || []);
    } catch (error) {
      console.error('Twitter search failed:', error);
      setError('Twitter search failed, please try again later');
    } finally {
      setLoading(false);
    }
  };

  const searchTwitterUser = async () => {
    if (!username.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/social-scraping/twitter/user/${encodeURIComponent(username)}?limit=20`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setTwitterPosts(data.tweets || []);
    } catch (error) {
      console.error('Twitter user search failed:', error);
      setError('Twitter user search failed, please try again later');
    } finally {
      setLoading(false);
    }
  };

  const searchReddit = async () => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/social-scraping/reddit/search?query=${encodeURIComponent(searchQuery)}&limit=20`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setRedditPosts(data.posts || []);
    } catch (error) {
      console.error('Reddit search failed:', error);
      setError('Reddit search failed, please try again later');
    } finally {
      setLoading(false);
    }
  };

  const searchSubreddit = async () => {
    if (!subreddit.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/social-scraping/reddit/subreddit/${encodeURIComponent(subreddit)}?limit=20`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setRedditPosts(data.posts || []);
    } catch (error) {
      console.error('Subreddit search failed:', error);
      setError('Subreddit search failed, please try again later');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString('zh-CN');
    } catch {
      return dateString;
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5" />
          Social Media Data Scraping
        </CardTitle>
        <CardDescription>
          Real-time scraping of Twitter and Reddit data, no API keys required
        </CardDescription>
        
        {/* Connection status indicators */}
        {connectionStatus && (
          <div className="flex gap-2 mt-2">
            <Badge variant={connectionStatus.twitter ? "default" : "secondary"}>
              <XLogo className="h-3 w-3 mr-1" />
              Twitter {connectionStatus.twitter ? 'Connected' : 'Disconnected'}
            </Badge>
            <Badge variant={connectionStatus.reddit ? "default" : "secondary"}>
              <RedditLogo className="h-3 w-3 mr-1" />
              Reddit {connectionStatus.reddit ? 'Connected' : 'Disconnected'}
            </Badge>
          </div>
        )}
      </CardHeader>
      
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="twitter" className="flex items-center gap-2">
              <XLogo className="h-4 w-4" />
              Twitter
            </TabsTrigger>
            <TabsTrigger value="reddit" className="flex items-center gap-2">
              <RedditLogo className="h-4 w-4" />
              Reddit
            </TabsTrigger>
          </TabsList>
          
          {/* Twitter Tab */}
          <TabsContent value="twitter" className="space-y-4">
            <div className="space-y-3">
              <div className="flex gap-2">
                <Input
                  placeholder="Search tweet content..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && searchTwitter()}
                />
                <Button onClick={searchTwitter} disabled={loading}>
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                </Button>
              </div>
              
              <div className="flex gap-2">
                <Input
                  placeholder="Username (without @)..."
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && searchTwitterUser()}
                />
                <Button onClick={searchTwitterUser} disabled={loading} variant="outline">
                  <User className="h-4 w-4" />
                </Button>
              </div>
            </div>
            
            {error && (
              <Alert>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            <ScrollArea className="h-[500px]">
              <div className="space-y-3">
                {twitterPosts.map((post) => (
                  <Card key={post.id} className="p-4">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <XLogo className="h-4 w-4" />
                          <span className="font-medium">@{post.user.username}</span>
                          <span className="text-sm text-muted-foreground">{post.user.displayname}</span>
                          <Badge variant="outline">{formatNumber(post.user.followers_count)} Followers</Badge>
                        </div>
                        <div className="flex items-center gap-1 text-sm text-muted-foreground">
                          <Calendar className="h-3 w-3" />
                          {formatDate(post.date)}
                        </div>
                      </div>
                      
                      <p className="text-sm leading-relaxed">{post.content}</p>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <Heart className="h-3 w-3" />
                            {formatNumber(post.metrics.like_count)}
                          </div>
                          <div className="flex items-center gap-1">
                            <Repeat2 className="h-3 w-3" />
                            {formatNumber(post.metrics.retweet_count)}
                          </div>
                          <div className="flex items-center gap-1">
                            <MessageCircle className="h-3 w-3" />
                            {formatNumber(post.metrics.reply_count)}
                          </div>
                        </div>
                        
                        <Button size="sm" variant="ghost" asChild>
                          <a href={post.url} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
                
                {twitterPosts.length === 0 && !loading && (
                  <div className="text-center text-muted-foreground py-8">
                    Search Twitter content or user tweets
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>
          
          {/* Reddit Tab */}
          <TabsContent value="reddit" className="space-y-4">
            <div className="space-y-3">
              <div className="flex gap-2">
                <Input
                  placeholder="Search Reddit posts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && searchReddit()}
                />
                <Button onClick={searchReddit} disabled={loading}>
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                </Button>
              </div>
              
              <div className="flex gap-2">
                <Input
                  placeholder="Subreddit name (without r/)..."
                  value={subreddit}
                  onChange={(e) => setSubreddit(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && searchSubreddit()}
                />
                <Button onClick={searchSubreddit} disabled={loading} variant="outline">
                  <RedditLogo className="h-4 w-4" />
                </Button>
              </div>
            </div>
            
            {error && (
              <Alert>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            <ScrollArea className="h-[500px]">
              <div className="space-y-3">
                {redditPosts.map((post) => (
                  <Card key={post.id} className="p-4">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <RedditLogo className="h-4 w-4" />
                          <span className="font-medium">r/{post.subreddit}</span>
                          <span className="text-sm text-muted-foreground">u/{post.author}</span>
                          {post.flair && (
                            <Badge variant="secondary" className="text-xs">{post.flair}</Badge>
                          )}
                          {post.is_nsfw && (
                            <Badge variant="destructive" className="text-xs">NSFW</Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-1 text-sm text-muted-foreground">
                          <Calendar className="h-3 w-3" />
                          {formatDate(post.created_utc)}
                        </div>
                      </div>
                      
                      <h3 className="font-medium leading-tight">{post.title}</h3>
                      
                      {post.content && (
                        <p className="text-sm text-muted-foreground leading-relaxed line-clamp-3">
                          {post.content}
                        </p>
                      )}
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <div className="flex items-center gap-1">
                            <span>↑</span>
                            {post.metrics.score}
                          </div>
                          <div className="flex items-center gap-1">
                            <MessageCircle className="h-3 w-3" />
                            {post.metrics.num_comments}
                          </div>
                          {post.metrics.upvote_ratio && (
                            <div className="flex items-center gap-1">
                              <span>👍</span>
                              {Math.round(post.metrics.upvote_ratio * 100)}%
                            </div>
                          )}
                        </div>
                        
                        <div className="flex gap-1">
                          <Button size="sm" variant="ghost" asChild>
                            <a href={post.permalink} target="_blank" rel="noopener noreferrer">
                              <ExternalLink className="h-3 w-3" />
                            </a>
                          </Button>
                          {post.url !== post.permalink && (
                            <Button size="sm" variant="ghost" asChild>
                              <a href={post.url} target="_blank" rel="noopener noreferrer">
                                <ExternalLink className="h-3 w-3" />
                              </a>
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
                
                {redditPosts.length === 0 && !loading && (
                  <div className="text-center text-muted-foreground py-8">
                    Search Reddit posts or browse Subreddit
                  </div>
                )}
              </div>
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default SocialScrapingPanel;