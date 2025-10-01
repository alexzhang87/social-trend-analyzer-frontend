import type { ActionableOpportunity } from "../declarations";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Target, Lightbulb, Rocket, Wrench } from "lucide-react";

interface OpportunitiesPanelProps {
  opportunities: ActionableOpportunity[];
}

const opportunityIcons = [
    <Lightbulb className="w-6 h-6 text-yellow-500" />,
    <Rocket className="w-6 h-6 text-green-500" />,
    <Wrench className="w-6 h-6 text-blue-500" />,
];

export function OpportunitiesPanel({ opportunities }: OpportunitiesPanelProps) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-gray-800 flex items-center">
          <div className="flex items-center justify-center bg-orange-100 rounded-full w-8 h-8 mr-3">
            <Rocket className="w-4 h-4 text-orange-600" />
          </div>
          Actionable Opportunities
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {opportunities && opportunities.length > 0 ? (
          opportunities.map((item, index) => (
            <div key={index} className="p-4 border rounded-lg bg-muted/40 flex items-start gap-4">
              <div className="p-2 bg-primary/10 rounded-lg mt-1">
                {opportunityIcons[index % opportunityIcons.length]}
              </div>
              <div>
                <h4 className="font-semibold text-gray-800">{item.opportunity}</h4>
                <p className="text-sm text-gray-600 mt-1 mb-2">
                  {item.description}
                </p>
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4 text-muted-foreground" />
                  <span className="text-xs font-semibold text-muted-foreground">TARGETS:</span>
                  <Badge variant="secondary">{item.targetPersona}</Badge>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center text-sm text-muted-foreground p-4">
            No specific business opportunities were identified.
          </div>
        )}
      </CardContent>
    </Card>
  );
}