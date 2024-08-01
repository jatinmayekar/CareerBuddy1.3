import React from 'react';

const PitchComparison = ({ originalPitch, userPitch }) => {
  const words = originalPitch.split(' ');
  const userWords = userPitch.split(' ');

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-bold mb-4">Pitch Comparison</h2>
      <div className="flex space-x-4">
        <div className="w-1/2">
          <h3 className="text-xl font-semibold mb-2">Original Pitch</h3>
          <p>
            {words.map((word, index) => (
              <span
                key={index}
                className={userWords.includes(word) ? 'text-green-600' : 'text-red-600'}
              >
                {word}{' '}
              </span>
            ))}
          </p>
        </div>
        <div className="w-1/2">
          <h3 className="text-xl font-semibold mb-2">Your Pitch</h3>
          <p>
            {userWords.map((word, index) => (
              <span
                key={index}
                className={words.includes(word) ? 'text-green-600' : 'text-red-600'}
              >
                {word}{' '}
              </span>
            ))}
          </p>
        </div>
      </div>
    </div>
  );
};

export default PitchComparison;