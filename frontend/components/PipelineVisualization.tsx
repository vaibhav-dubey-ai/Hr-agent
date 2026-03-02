'use client';

export default function PipelineVisualization() {
  const states = [
    { name: 'Applied', icon: '📝', color: 'bg-blue-500' },
    { name: 'Screened', icon: '👀', color: 'bg-purple-500' },
    { name: 'Interview', icon: '🎤', color: 'bg-orange-500' },
    { name: 'Interviewed', icon: '✅', color: 'bg-yellow-500' },
    { name: 'Offer', icon: '💼', color: 'bg-green-500' },
    { name: 'Hired', icon: '🎉', color: 'bg-emerald-500' },
  ];

  return (
    <div className="overflow-x-auto">
      <div className="flex items-center gap-4 min-w-max py-8">
        {states.map((state, idx) => (
          <div key={state.name} className="flex items-center gap-4">
            <div className="flex flex-col items-center">
              <div className={`w-16 h-16 rounded-full ${state.color} flex items-center justify-center text-3xl shadow-lg`}>
                {state.icon}
              </div>
              <p className="text-sm font-semibold mt-3 text-center whitespace-nowrap">
                {state.name}
              </p>
            </div>
            {idx < states.length - 1 && (
              <div className="w-12 h-1 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
            )}
          </div>
        ))}
      </div>
      <div className="text-sm text-gray-600 dark:text-gray-400 mt-4">
        <p>• Candidates can be rejected at any stage</p>
        <p>• Each transition is recorded with timestamp and reason</p>
      </div>
    </div>
  );
}
