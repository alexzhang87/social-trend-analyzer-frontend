import { ThemeProvider } from "@/components/theme-provider"
import { TrendAnalyzer } from "@/components/trend-analyzer"

function App() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="trend-analyzer-theme">
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <TrendAnalyzer />
      </div>
    </ThemeProvider>
  )
}

export default App