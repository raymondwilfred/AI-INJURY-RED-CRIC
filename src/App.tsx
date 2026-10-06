import { type ReactNode } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ErrorBoundary } from '@/components/error-boundary';
import { Toaster } from '@/components/ui/toaster';
import { TooltipProvider } from '@/components/ui/tooltip';
import NotFound from '@/pages/not-found';
import { Route, Switch, useLocation, Router as WouterRouter } from 'wouter';
import { AppShell } from '@/components/AppShell';
import {
  ArchitecturePage, DashboardPage, MethodologyPage, ModelComparisonPage, PlayerDetailsPage,
  PlayersPage, StructuredScreeningPage, VideoAnalysisPage,
} from '@/pages/ResearchPages';

const queryClient = new QueryClient();

function RoutedErrorBoundary({ children }: { children: ReactNode }) {
  const [location] = useLocation();
  return <ErrorBoundary resetKey={location}>{children}</ErrorBoundary>;
}

function Router() {
  return (
    <AppShell>
      <RoutedErrorBoundary>
        <Switch>
          <Route path="/" component={DashboardPage} />
          <Route path="/players" component={PlayersPage} />
          <Route path="/player-details" component={PlayerDetailsPage} />
          <Route path="/structured-screening" component={StructuredScreeningPage} />
          <Route path="/model-comparison" component={ModelComparisonPage} />
          <Route path="/video-analysis" component={VideoAnalysisPage} />
          <Route path="/system-architecture" component={ArchitecturePage} />
          <Route path="/methodology" component={MethodologyPage} />
          <Route component={NotFound} />
        </Switch>
      </RoutedErrorBoundary>
    </AppShell>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, '')}>
          <Router />
        </WouterRouter>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
