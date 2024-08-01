import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ProgressTracking = ({ practiceHistory }) => {
  const chartData = practiceHistory.map((practice, index) => ({
    attempt: index + 1,
    audioScore: practice.audioAnalysis.topEmotions[0][1],
    videoScore: practice.videoAnalysis.topEmotions[0][1],
  }));

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-bold mb-4">Your Progress</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="attempt" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="audioScore" stroke="#8884d8" name="Audio Score" />
          <Line type="monotone" dataKey="videoScore" stroke="#82ca9d" name="Video Score" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ProgressTracking;