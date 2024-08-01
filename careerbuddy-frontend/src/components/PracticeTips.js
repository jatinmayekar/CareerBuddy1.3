import React from 'react';

const PracticeTips = () => {
  const tips = [
    "Start with a strong opening that grabs attention.",
    "Maintain eye contact with your audience or camera.",
    "Use confident body language and gestures.",
    "Speak clearly and at a moderate pace.",
    "Emphasize key points with your tone and inflection.",
    "Practice your pitch in front of a mirror or with friends.",
    "Be concise and stay within the 30-60 second time frame.",
    "End with a clear call-to-action or next steps.",
    "Show enthusiasm and passion for your subject.",
    "Tailor your pitch to the specific job or company.",
  ];

  return (
    <div className="mt-8 bg-blue-100 p-6 rounded-lg">
      <h2 className="text-2xl font-bold mb-4">Practice Tips</h2>
      <ul className="list-disc pl-5 space-y-2">
        {tips.map((tip, index) => (
          <li key={index} className="text-blue-800">{tip}</li>
        ))}
      </ul>
    </div>
  );
};

export default PracticeTips;