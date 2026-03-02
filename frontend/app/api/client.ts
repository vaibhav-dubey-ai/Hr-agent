/**
 * API Client for HR Agent Backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        error: data.detail || data.error || 'An error occurred',
        status: response.status,
      };
    }

    return {
      data,
      status: response.status,
    };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Network error',
      status: 0,
    };
  }
}

// Ranking API
export async function rankResumes(jdText: string, topK: number = 20) {
  return fetchAPI('/api/rank', {
    method: 'POST',
    body: JSON.stringify({
      jd_text: jdText,
      top_k: topK,
    }),
  });
}

// Leave API
export async function submitLeaveRequest(
  employeeName: string,
  leaveType: string,
  startDate: string,
  endDate: string,
  daysRequested: number
) {
  return fetchAPI('/api/leave', {
    method: 'POST',
    body: JSON.stringify({
      employee_name: employeeName,
      leave_type: leaveType,
      start_date: startDate,
      end_date: endDate,
      days_requested: daysRequested,
    }),
  });
}

// Scheduling API
export async function registerInterviewerAvailability(
  interviewerId: string,
  availableDates: string[],
  availableTimes: string[]
) {
  return fetchAPI('/api/schedule/availability', {
    method: 'POST',
    body: JSON.stringify({
      interviewer_id: interviewerId,
      available_dates: availableDates,
      available_times: availableTimes,
    }),
  });
}

export async function scheduleInterview(
  candidateId: string,
  interviewerId: string,
  preferredDate: string,
  preferredTime: string
) {
  return fetchAPI('/api/schedule', {
    method: 'POST',
    body: JSON.stringify({
      candidate_id: candidateId,
      interviewer_id: interviewerId,
      preferred_date: preferredDate,
      preferred_time: preferredTime,
    }),
  });
}

// Pipeline API
export async function transitionCandidate(
  candidateId: string,
  newState: string,
  reason: string = ''
) {
  return fetchAPI('/api/transition', {
    method: 'POST',
    body: JSON.stringify({
      candidate_id: candidateId,
      new_state: newState,
      reason: reason,
    }),
  });
}

export async function getCandidateState(candidateId: string) {
  return fetchAPI(`/api/state/${candidateId}`, {
    method: 'GET',
  });
}

// Questions API
export async function generateInterviewQuestions(
  jdText: string,
  candidateName: string = '',
  candidateBackground: string = ''
) {
  return fetchAPI('/api/generate-questions', {
    method: 'POST',
    body: JSON.stringify({
      jd_text: jdText,
      candidate_name: candidateName,
      candidate_background: candidateBackground,
    }),
  });
}

// Export API
export async function exportResults() {
  return fetchAPI('/api/export', {
    method: 'GET',
  });
}

// Health check
export async function healthCheck() {
  return fetchAPI('/health', {
    method: 'GET',
  });
}
