import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 応募者API
export const applicantsApi = {
  // 一覧取得
  getAll: (params = {}) => api.get('/api/applicants/', { params }),

  // 詳細取得
  getById: (id) => api.get(`/api/applicants/${id}`),

  // 新規作成
  create: (data) => api.post('/api/applicants/', data),

  // 更新
  update: (id, data) => api.patch(`/api/applicants/${id}`, data),

  // 削除
  delete: (id) => api.delete(`/api/applicants/${id}`),

  // 履歴書アップロード
  uploadResume: (id, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/api/applicants/${id}/upload-resume`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

// 評価API
export const evaluationApi = {
  // データ抽出
  extractData: (applicantId, resumeUrl) =>
    api.post('/api/evaluation/extract-data', { applicant_id: applicantId, resume_url: resumeUrl }),

  // 評価実行
  evaluate: (applicantId, skillRatio = null, mindsetRatio = null) =>
    api.post('/api/evaluation/evaluate', {
      applicant_id: applicantId,
      skill_ratio: skillRatio,
      mindset_ratio: mindsetRatio,
    }),

  // 比率更新
  updateRatio: (applicantId, skillRatio, mindsetRatio) =>
    api.post(`/api/evaluation/${applicantId}/update-ratio`, {
      skill_ratio: skillRatio,
      mindset_ratio: mindsetRatio,
    }),

  // 手動評価を保存
  saveManualEvaluation: (applicantId, data) =>
    api.post(`/api/evaluation/${applicantId}/manual`, data),
}

// 面接API
export const interviewApi = {
  // 質問生成
  generateQuestions: (applicantId, questionCount = 10) =>
    api.post('/api/interview/generate-questions', {
      applicant_id: applicantId,
      question_count: questionCount,
    }),

  // 質問取得
  getQuestions: (applicantId) => api.get(`/api/interview/${applicantId}/questions`),
}

// バッチAPI
export const batchApi = {
  // CSVアップロード
  uploadCsv: (file, skillRatio = 0.2, mindsetRatio = 0.8) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('skill_ratio', skillRatio)
    formData.append('mindset_ratio', mindsetRatio)
    return api.post('/api/batch/upload-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // 結果エクスポート
  exportResults: (params = {}) => api.get('/api/batch/export-results', { params }),
}

// 評価基準API
export const criteriaApi = {
  // ファイルアップロード
  uploadFile: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/api/criteria/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // アップロード済みファイルの一覧を取得
  getAll: () => api.get('/api/criteria/'),

  // 指定したファイルを解析して取得
  getByName: (filename) => api.get(`/api/criteria/${filename}`),

  // ファイルを削除
  deleteFile: (filename) => api.delete(`/api/criteria/${filename}`),
}

// 選考ステージAPI
export const stagesApi = {
  // 全ステージを取得
  getAll: () => api.get('/api/stages/'),

  // ステージを新規作成
  create: (data) => api.post('/api/stages/', data),
}

export default api
