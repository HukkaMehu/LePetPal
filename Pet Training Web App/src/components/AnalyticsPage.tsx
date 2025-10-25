import { useState } from 'react';
import { Card } from './ui/card';
import { Progress } from './ui/progress';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Clock, Activity, TrendingUp, Trophy, AlertCircle, Calendar as CalendarIcon } from 'lucide-react';
import { useAnalytics } from '../hooks/useAnalytics';
import { Button } from './ui/button';
import { AnalyticsSkeleton } from './LoadingStates';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { Calendar } from './ui/calendar';
import { format, differenceInDays } from 'date-fns';

type DateRange = {
  from: Date;
  to: Date;
};

export default function AnalyticsPage() {
  const [days, setDays] = useState(7);
  const [customRange, setCustomRange] = useState<DateRange | undefined>();
  const [isCustom, setIsCustom] = useState(false);
  
  // Calculate days from custom range if set
  const effectiveDays = isCustom && customRange 
    ? differenceInDays(customRange.to, customRange.from) + 1 
    : days;
  
  const { data, loading, error, refetch } = useAnalytics({ days: effectiveDays });

  const handlePresetDays = (presetDays: number) => {
    setDays(presetDays);
    setIsCustom(false);
    setCustomRange(undefined);
  };

  const handleCustomRange = (range: DateRange | undefined) => {
    if (range?.from && range?.to) {
      setCustomRange(range);
      setIsCustom(true);
      const daysDiff = differenceInDays(range.to, range.from) + 1;
      setDays(daysDiff);
    }
  };

  // Calculate stats from real data
  const calculateStats = () => {
    if (!data) {
      return [
        { label: 'Avg. Time in Frame', value: '--', icon: Clock },
        { label: 'Total Activity', value: '--', icon: Activity },
        { label: 'Commands Learned', value: '--', icon: TrendingUp },
      ];
    }

    // Calculate average time in frame per day
    const totalTimeInFrame = data.activityLevel.reduce((sum, day) => sum + day.calm + day.active, 0);
    const avgTimeInFrameHours = (totalTimeInFrame / days / 60).toFixed(1);

    // Calculate total activity minutes
    const totalActivity = data.activityLevel.reduce((sum, day) => sum + day.active, 0);

    // Count total behaviors as a proxy for commands learned
    const totalBehaviors = data.behaviors.reduce((sum, behavior) => sum + behavior.count, 0);

    return [
      { label: 'Avg. Time in Frame', value: `${avgTimeInFrameHours} hrs`, icon: Clock },
      { label: 'Total Activity', value: `${totalActivity.toLocaleString()} min`, icon: Activity },
      { label: 'Total Behaviors', value: totalBehaviors.toString(), icon: TrendingUp },
    ];
  };

  const stats = calculateStats();

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-border bg-card px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2>Analytics</h2>
            <p className="text-sm text-muted-foreground">
              {isCustom && customRange
                ? `${format(customRange.from, 'MMM d')} - ${format(customRange.to, 'MMM d, yyyy')}`
                : `Last ${days} days`}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant={!isCustom && days === 7 ? 'default' : 'outline'}
              size="sm"
              onClick={() => handlePresetDays(7)}
            >
              7 days
            </Button>
            <Button
              variant={!isCustom && days === 30 ? 'default' : 'outline'}
              size="sm"
              onClick={() => handlePresetDays(30)}
            >
              30 days
            </Button>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant={isCustom ? 'default' : 'outline'}
                  size="sm"
                  className="gap-2"
                >
                  <CalendarIcon className="h-4 w-4" />
                  Custom
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="end">
                <Calendar
                  mode="range"
                  selected={customRange}
                  onSelect={handleCustomRange}
                  numberOfMonths={2}
                  disabled={(date: Date) => date > new Date()}
                />
              </PopoverContent>
            </Popover>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {/* Loading State */}
        {loading && (
          <AnalyticsSkeleton />
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-md">
              <AlertCircle className="w-8 h-8 mx-auto mb-2 text-destructive" />
              <p className="text-sm text-muted-foreground mb-4">
                Failed to load analytics data: {error.message}
              </p>
              <Button onClick={refetch} variant="outline" size="sm">
                Try Again
              </Button>
            </div>
          </div>
        )}

        {/* Data Content */}
        {!loading && !error && data && (
        <div className="max-w-6xl mx-auto space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-3 gap-4">
            {stats.map((stat) => (
              <Card key={stat.label} className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
                    <stat.icon className="w-5 h-5 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                    <p className="text-xl">{stat.value}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Skill Learning Progress */}
          <Card className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <Trophy className="w-5 h-5 text-muted-foreground" />
              <h3>Skill Learning Progress</h3>
            </div>
            <div className="space-y-4">
              {data.skillProgress.length > 0 ? (
                data.skillProgress.map((skill) => {
                  const percentage = skill.total > 0 
                    ? Math.round((skill.success / skill.total) * 100) 
                    : 0;
                  return (
                    <div key={skill.skill} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">{skill.skill}</span>
                        <span className="text-sm text-muted-foreground">
                          {skill.success}/{skill.total} ({percentage}%)
                        </span>
                      </div>
                      <Progress value={percentage} className="h-2" />
                    </div>
                  );
                })
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No skill progress data available yet
                </p>
              )}
            </div>
          </Card>

          {/* Charts */}
          <div className="grid grid-cols-2 gap-6">
            <Card className="p-6">
              <h3 className="mb-4">Activity Level</h3>
              {data.activityLevel.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={data.activityLevel}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="date" stroke="var(--color-muted-foreground)" />
                    <YAxis stroke="var(--color-muted-foreground)" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--color-card)',
                        border: '1px solid var(--color-border)',
                        borderRadius: '0.5rem',
                      }}
                    />
                    <Bar dataKey="calm" fill="var(--color-chart-1)" name="Calm" />
                    <Bar dataKey="active" fill="var(--color-chart-2)" name="Active" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[250px] flex items-center justify-center text-sm text-muted-foreground">
                  No activity data available
                </div>
              )}
            </Card>

            <Card className="p-6">
              <h3 className="mb-4">Time in Frame</h3>
              {data.timeInFrame.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={data.timeInFrame.slice(6, 22)}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="hour" stroke="var(--color-muted-foreground)" />
                    <YAxis stroke="var(--color-muted-foreground)" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--color-card)',
                        border: '1px solid var(--color-border)',
                        borderRadius: '0.5rem',
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="minutes"
                      stroke="var(--color-chart-3)"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[250px] flex items-center justify-center text-sm text-muted-foreground">
                  No time in frame data available
                </div>
              )}
            </Card>

            <Card className="p-6">
              <h3 className="mb-4">Fetch Success Rate</h3>
              {data.fetchSuccess.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={data.fetchSuccess}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="date" stroke="var(--color-muted-foreground)" />
                    <YAxis stroke="var(--color-muted-foreground)" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--color-card)',
                        border: '1px solid var(--color-border)',
                        borderRadius: '0.5rem',
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="success"
                      stroke="var(--color-chart-4)"
                      strokeWidth={2}
                      name="Success"
                    />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[250px] flex items-center justify-center text-sm text-muted-foreground">
                  No fetch success data available
                </div>
              )}
            </Card>

            <Card className="p-6">
              <h3 className="mb-4">Bark Frequency</h3>
              {data.barkFrequency.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={data.barkFrequency}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="hour" stroke="var(--color-muted-foreground)" />
                    <YAxis stroke="var(--color-muted-foreground)" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--color-card)',
                        border: '1px solid var(--color-border)',
                        borderRadius: '0.5rem',
                      }}
                    />
                    <Bar dataKey="count" fill="var(--color-chart-5)" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[250px] flex items-center justify-center text-sm text-muted-foreground">
                  No bark frequency data available
                </div>
              )}
            </Card>
          </div>
        </div>
        )}
      </div>
    </div>
  );
}
