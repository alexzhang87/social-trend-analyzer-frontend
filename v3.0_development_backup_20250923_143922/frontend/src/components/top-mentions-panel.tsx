import type { TopMention } from "../declarations";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { XLogo } from "@/components/ui/x-logo";
import { RedditLogo } from "@/components/ui/reddit-logo";
import { ThumbsUp, MessageCircle, TrendingUp, TrendingDown, MinusCircle } from "lucide-react";

interface TopMentionsPanelProps {
  mentions: TopMention[];
}

const PlatformIcon = ({ platform }: { platform: string }) => {
  if (platform.toLowerCase() === 'x' || platform.toLowerCase() === 'twitter') return <XLogo className="w-4 h-4 text-gray-700" />;
  if (platform.toLowerCase() === 'reddit') return <RedditLogo className="w-4 h-4 text-red-500" />;
  return <MessageCircle className="w-4 h-4 text-gray-700" />;
};

const SentimentIndicator = ({ sentiment }: { sentiment: string }) => {
    switch (sentiment.toLowerCase()) {
        case 'positive':
            return <div className="flex items-center gap-1 text-xs text-green-600"><TrendingUp className="w-3.5 h-3.5" /> Positive</div>;
        case 'negative':
            return <div className="flex items-center gap-1 text-xs text-red-600"><TrendingDown className="w-3.5 h-3.5" /> Negative</div>;
        default:
            return <div className="flex items-center gap-1 text-xs text-gray-700"><MinusCircle className="w-3.5 h-3.5" /> Neutral</div>;
    }
};

export function TopMentionsPanel({ mentions }: TopMentionsPanelProps) {
  // Simple function to calculate text similarity
  const calculateTextSimilarity = (text1: string, text2: string): number => {
    const words1 = text1.split(' ').filter(w => w.length > 2);
    const words2 = text2.split(' ').filter(w => w.length > 2);
    
    if (words1.length === 0 || words2.length === 0) return 0;
    
    const commonWords = words1.filter(word => words2.includes(word));
    return commonWords.length / Math.max(words1.length, words2.length);
  };
  
  // Enhanced deduplication logic: based on text content similarity and author deduplication
  const uniqueMentions = mentions ? mentions.filter((mention, index, self) => {
    const currentText = mention.text?.trim()?.toLowerCase() || '';
    const currentAuthor = mention.author;
    
    // Check if there's similar content from the same author
    const isDuplicate = self.slice(0, index).some(m => {
      const existingText = m.text?.trim()?.toLowerCase() || '';
      const existingAuthor = m.author;
      
      // Same author and identical text
      if (existingAuthor === currentAuthor && existingText === currentText) {
        return true;
      }
      
      // Check text similarity (simple containment check)
      if (currentText.length > 20 && existingText.length > 20) {
        const similarity = calculateTextSimilarity(currentText, existingText);
        if (similarity > 0.8) {
          return true;
        }
      }
      
      return false;
    });
    
    return !isDuplicate;
  }) : [];

  // Fix X platform links
  const getValidUrl = (mention: TopMention) => {
    if (!mention.url || mention.url === '' || mention.url.includes('user_') || mention.url.includes('1234567890')) {
      // If it's an invalid mock link, generate correct link based on platform
      if (mention.platform.toLowerCase() === 'x' || mention.platform.toLowerCase() === 'twitter') {
        return `https://x.com/${mention.author}`;
      } else if (mention.platform.toLowerCase() === 'reddit') {
        return `https://reddit.com/user/${mention.author}`;
      }
      return '#'; // Default return empty link
    }
    return mention.url;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-foreground flex items-center">
          <div className="flex items-center justify-center bg-accent/20 rounded-full w-8 h-8 mr-3">
            <MessageCircle className="w-4 h-4 text-accent" />
          </div>
          Top Mentions & Evidence
        </CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {uniqueMentions && uniqueMentions.length > 0 ? (
          uniqueMentions.map((mention, index) => (
            <a 
              key={index}
              href={getValidUrl(mention)}
              target="_blank"
              rel="noopener noreferrer"
              className="block p-4 border rounded-xl bg-white hover:shadow-lg hover:border-primary/50 transition-all duration-200 group"
              onClick={(e) => {
                const url = getValidUrl(mention);
                if (url === '#') {
                  e.preventDefault();
                }
              }}
            >
              <div className="flex flex-col h-full">
                <div className="flex items-center gap-3 mb-3">
                  <Avatar className="w-10 h-10 border">
                    <AvatarImage src={mention.author ? `https://avatar.vercel.sh/${mention.author}` : ''} alt={mention.author || 'Unknown author'} />
                    <AvatarFallback>{mention.author ? mention.author.substring(0, 2).toUpperCase() : '??'}</AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="flex justify-between items-center">
                        <span className="font-semibold text-sm text-gray-900">{mention.author || 'Unknown Author'}</span>
                        <PlatformIcon platform={mention.platform} />
                    </div>
                    <span className="text-xs text-gray-700">@{mention.author || 'unknown'}</span>
                  </div>
                </div>

                <p className="text-sm text-gray-700 flex-grow">{mention.text || 'No content available'}</p>
                
                <div className="flex justify-between items-center mt-4 pt-3 border-t">
                    <div className="flex items-center gap-1.5 text-sm font-semibold text-gray-800">
                        <ThumbsUp className="w-4 h-4 text-gray-600 group-hover:text-primary transition-colors" />
                        {mention.likes ? mention.likes.toLocaleString() : '0'}
                    </div>
                    <SentimentIndicator sentiment={mention.sentiment || 'neutral'} />
                </div>
              </div>
            </a>
          ))
        ) : (
          <div className="col-span-full text-center text-sm text-muted-foreground p-8">
            No top mentions were found.
          </div>
        )}
      </CardContent>
    </Card>
  );
}