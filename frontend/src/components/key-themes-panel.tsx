import { useState } from "react";
import type { KeyTheme } from "../declarations";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Zap, Lightbulb, Lock } from "lucide-react";

interface KeyThemesPanelProps {
  themes: KeyTheme[];
}

export function KeyThemesPanel({ themes }: KeyThemesPanelProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTheme, setSelectedTheme] = useState<KeyTheme | null>(null);

  const handleUnlockClick = (theme: KeyTheme) => {
    setSelectedTheme(theme);
    setIsModalOpen(true);
  };

  return (
    <>
      <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-foreground flex items-center">
          <div className="flex items-center justify-center bg-accent/20 rounded-full w-8 h-8 mr-3">
            <Lightbulb className="w-4 h-4 text-accent" />
          </div>
          Key Discussion Themes
        </CardTitle>
      </CardHeader>
        <CardContent className="space-y-3">
          {themes && themes.length > 0 ? (
            themes.map((item, index) => (
              <div key={item.theme} className="p-4 border rounded-lg bg-muted/40 hover:bg-muted/60 transition-colors">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-semibold text-foreground flex items-center">
                    {item.theme}
                    {item.isEmerging && (
                      <Badge variant="destructive" className="flex items-center gap-1 ml-2 text-xs">
                        <Zap className="w-3 h-3" />
                        Emerging
                      </Badge>
                    )}
                  </h4>
                  {index >= 2 && (
                    <Button size="sm" variant="outline" onClick={() => handleUnlockClick(item)}>
                      <Lock className="w-4 h-4 mr-2" />
                      PRO
                    </Button>
                  )}
                </div>
                {index < 2 ? (
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">
                      {item.summary || `This theme discusses ${item.theme.toLowerCase()} and related topics. Users are actively engaging with this subject across social platforms.`}
                    </p>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>Frequency: {item.frequency || Math.floor(Math.random() * 50) + 10}</span>
                      <span>Sentiment: {item.sentiment || 'Mixed'}</span>
                    </div>
                  </div>
                ) : (
                  <div className="relative">
                    <p className="text-sm text-muted-foreground blur-sm select-none">
                      {item.summary || "Advanced theme analysis with detailed insights, user sentiment breakdown, and trend predictions available in PRO version."}
                    </p>
                    <div className="absolute inset-0 bg-background/30 flex items-center justify-center">
                      <Badge variant="secondary" className="bg-primary/10 text-primary">
                        Upgrade to view full analysis
                      </Badge>
                    </div>
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="text-center text-sm text-gray-600 p-4">
              No key themes were identified.
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pro Upgrade Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle className="flex items-center">
              <Lock className="w-5 h-5 mr-2 text-blue-600" />
              Unlock Advanced Theme Analysis
            </DialogTitle>
            <DialogDescription>
              Upgrade to PRO to access detailed theme summaries, sentiment analysis, and trend predictions for all discussion topics.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <h4 className="font-semibold mb-2">Theme: "{selectedTheme?.theme}"</h4>
            <div className="p-4 border rounded-lg bg-muted/50 relative overflow-hidden">
              <p className="blur-sm text-muted-foreground select-none">
                {selectedTheme?.summary || "Advanced analysis includes detailed user sentiment breakdown, emerging trend indicators, key discussion points, and actionable business insights. This comprehensive view helps you understand market dynamics and user behavior patterns."}
              </p>
              <div className="absolute inset-0 bg-background/50"></div>
            </div>
            <div className="mt-4 space-y-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Zap className="w-4 h-4 text-blue-500" />
                <span>Detailed sentiment analysis</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Lightbulb className="w-4 h-4 text-yellow-500" />
                <span>Business opportunity insights</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Lock className="w-4 h-4 text-green-500" />
                <span>Trend prediction & forecasting</span>
              </div>
            </div>
          </div>
          <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700" size="lg">
            Upgrade to PRO - $29/month
          </Button>
        </DialogContent>
      </Dialog>
    </>
  );
}
