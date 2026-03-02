import { useState, useEffect } from 'react';

interface PipelineStateData {
  candidate_id: string;
  current_state: string;
  history: Array<{
    state: string;
    timestamp: string;
    reason?: string;
    action?: string;
  }>;
}

export function usePipelineState(candidateId: string) {
  const [state, setState] = useState<string>('applied');
  const [history, setHistory] = useState<PipelineStateData['history']>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchState = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/state/${candidateId}`);
      const data = await response.json();

      if (data.success && data.state) {
        setState(data.state.current_state);
        setHistory(data.state.history);
        setError(null);
      } else {
        setError('Failed to fetch state');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error fetching state');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchState();
  }, [candidateId]);

  const transitionTo = async (
    newState: string,
    reason: string
  ): Promise<{ success: boolean; error?: string }> => {
    setLoading(true);

    try {
      const response = await fetch('/api/transition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidate_id: candidateId,
          new_state: newState,
          reason,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setState(newState);
        if (data.state) {
          setHistory(data.state.history);
        }
        setError(null);
        return { success: true };
      } else {
        const errorMsg = data.message || 'Transition failed';
        setError(errorMsg);
        return { success: false, error: errorMsg };
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Network error';
      setError(errorMsg);
      return { success: false, error: errorMsg };
    } finally {
      setLoading(false);
    }
  };

  return {
    state,
    history,
    loading,
    error,
    fetchState,
    transitionTo,
  };
}
