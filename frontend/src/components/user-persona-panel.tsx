import type { UserPersonaSnapshot } from "../declarations";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Users, CheckCircle, User, Heart } from "lucide-react";

interface UserPersonaPanelProps {
  snapshot: UserPersonaSnapshot;
}

const personaIcons = [
    <Users className="w-5 h-5 text-blue-500" />,
    <User className="w-5 h-5 text-green-500" />,
    <Heart className="w-5 h-5 text-red-500" />,
];

export function UserPersonaPanel({ snapshot }: UserPersonaPanelProps) {
  if (!snapshot || !snapshot.personas) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="text-base font-medium flex items-center">
              <Users className="w-5 h-5 mr-2" /> User Persona Snapshot
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500">No persona data available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-base font-medium flex items-center">
            <Users className="w-5 h-5 mr-2" /> User Persona Snapshot
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <h4 className="font-semibold text-base mb-3">Identified Personas:</h4>
          <div className="flex flex-wrap gap-3">
            {snapshot.personas.map((persona, index) => (
              <div key={persona} className="flex items-center gap-2 text-sm font-medium text-gray-800 bg-muted/70 px-3 py-1.5 rounded-full shadow-sm">
                {personaIcons[index % personaIcons.length]}
                {persona}
              </div>
            ))}
          </div>
        </div>
        <div>
          <h4 className="font-semibold text-base mb-3">Their Core Needs & Wants:</h4>
          <ul className="space-y-2.5">
            {snapshot.coreNeeds.map((need) => (
              <li key={need} className="flex items-start gap-3">
                <CheckCircle className="w-4 h-4 text-green-600 mt-1 flex-shrink-0" />
                <span className="text-sm text-gray-700">{need}</span>
              </li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
