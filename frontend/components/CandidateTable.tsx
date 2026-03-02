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

interface CandidateTableProps {
  candidates: Candidate[];
  onSelect: (candidate: Candidate) => void;
}

export default function CandidateTable({ candidates, onSelect }: CandidateTableProps) {
  return (
    <div className="overflow-x-auto">
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Candidate Name</th>
            <th>Experience</th>
            <th>Education</th>
            <th>Match Score</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {candidates.map((candidate) => (
            <tr key={candidate.candidate_id}>
              <td>
                <span className="font-bold text-primary">#{candidate.rank}</span>
              </td>
              <td>
                <span className="font-medium">{candidate.name}</span>
              </td>
              <td>{candidate.reasoning.experience || 'N/A'}</td>
              <td>{candidate.reasoning.degree || 'N/A'}</td>
              <td>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-primary h-2 rounded-full"
                      style={{ width: `${candidate.normalized_score * 100}%` }}
                    ></div>
                  </div>
                  <span className="font-bold min-w-12">
                    {(candidate.normalized_score * 100).toFixed(0)}%
                  </span>
                </div>
              </td>
              <td>
                <button
                  onClick={() => onSelect(candidate)}
                  className="btn-ghost text-sm"
                >
                  Details →
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
