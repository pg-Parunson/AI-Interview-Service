import { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

const StatisticCard = ({ title, value, description }) => (
  <div className="bg-white rounded-lg p-6 shadow-md">
    <h3 className="text-lg font-semibold text-gray-700">{title}</h3>
    <p className="text-3xl font-bold text-blue-600 my-2">{value}</p>
    <p className="text-sm text-gray-500">{description}</p>
  </div>
);

const defaultStatistics = {
  total_interviews: 0,
  completion_rate: 0,
  position_distribution: {
    "프론트엔드": 0,
    "백엔드": 0,
    "풀스택": 0
  },
  success_rate: 0
};

const StatisticsDashboard = ({ statistics = defaultStatistics }) => {
  if (!statistics) {
    return (
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-yellow-700">통계 데이터를 불러올 수 없습니다.</p>
      </div>
    );
  }

  const {
    total_interviews = 0,
    completion_rate = 0,
    position_distribution = {},
    success_rate = 0
  } = statistics;

  const safePositionDistribution = Object.keys(position_distribution).length > 0
    ? position_distribution
    : defaultStatistics.position_distribution;

  const chartData = Object.entries(safePositionDistribution).map(([position, count]) => ({
    name: position,
    value: count || 0
  }));

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">📊 면접 통계</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatisticCard
          title="총 면접 수"
          value={total_interviews.toLocaleString()}
          description="지금까지 진행된 면접의 총 횟수"
        />
        <StatisticCard
          title="완료율"
          value={`${completion_rate.toLocaleString()}%`}
          description="전체 면접 중 완료된 면접의 비율"
        />
        <StatisticCard
          title="성공률"
          value={`${success_rate.toLocaleString()}%`}
          description="완료된 면접 중 합격 기준을 통과한 비율"
        />
      </div>

      {chartData.length > 0 && (
        <div className="bg-white rounded-lg p-6 shadow-md">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">포지션별 분포</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatisticsDashboard;