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
import { Clock, Activity, TrendingUp, Trophy } from 'lucide-react';
import { generateMockAnalytics } from '../lib/mockData';

export default function AnalyticsPage() {
  const [data] = useState(generateMockAnalytics());

  const stats = [
    { label: 'Avg. Time in Frame', value: '6.2 hrs', icon: Clock },
    { label: 'Total Activity', value: '1,247 min', icon: Activity },
    { label: 'Commands Learned', value: '24', icon: TrendingUp },
  ];

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-border bg-card px-6 py-4">
        <div>
          <h2>Analytics</h2>
          <p className="text-sm text-muted-foreground">Last 7 days</p>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
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
              {data.skillProgress.map((skill) => (
                <div key={skill.skill} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">{skill.skill}</span>
                    <span className="text-sm text-muted-foreground">
                      {skill.success}%
                    </span>
                  </div>
                  <Progress value={skill.success} className="h-2" />
                </div>
              ))}
            </div>
          </Card>

          {/* Charts */}
          <div className="grid grid-cols-2 gap-6">
            <Card className="p-6">
              <h3 className="mb-4">Activity Level</h3>
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
            </Card>

            <Card className="p-6">
              <h3 className="mb-4">Time in Frame</h3>
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
            </Card>

            <Card className="p-6">
              <h3 className="mb-4">Fetch Success Rate</h3>
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
            </Card>

            <Card className="p-6">
              <h3 className="mb-4">Bark Frequency</h3>
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
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
