'use client';

interface Candidate {
  rank: number;
  candidate_id: number;
  name: string;
  score: number;
  normalized_score: number;
  reasoning: Record<string, any>;
  target_job: string;
}

interface RankingModalProps {
  candidate: Candidate;
  onClose: () => void;
}

export default function RankingModal({ candidate, onClose }: RankingModalProps) {
  return (
    <div className="modal" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="p-8">
          {/* Header */}
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-3xl font-bold mb-2">{candidate.name}</h2>
              <div className="flex items-center gap-3">
                <span className="text-4xl font-bold text-primary">
                  {(candidate.normalized_score * 100).toFixed(0)}%
                </span>
                <span className="badge-success">Match Score</span>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-2xl text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
            >
              ×
            </button>
          </div>

          {/* Details */}
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-bold mb-3">Target Role</h3>
              <p className="text-gray-600 dark:text-gray-400">
                {candidate.target_job}
              </p>
            </div>

            <div>
              <h3 className="text-lg font-bold mb-3">Reasoning</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Embedding Match</p>
                  <p className="text-2xl font-bold text-primary">
                    {candidate.reasoning.embedding_match}
                  </p>
                </div>
                <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Experience</p>
                  <p className="text-xl font-bold">
                    {candidate.reasoning.experience}
                  </p>
                </div>
                <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Education</p>
                  <p className="text-xl font-bold">
                    {candidate.reasoning.degree}
                  </p>
                </div>
                <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Certifications</p>
                  <p className="text-xl font-bold">
                    {candidate.reasoning.certifications}
                  </p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-bold mb-3">Key Skills</h3>
              <div className="flex flex-wrap gap-2">
                {candidate.reasoning.skills?.split(',').map((skill: string, idx: number) => (
                  <span key={idx} className="badge">
                    {skill.trim()}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 mt-8">
            <button className="btn-primary flex-1">
              Proceed to Interview
            </button>
            <button onClick={onClose} className="btn-ghost flex-1">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
