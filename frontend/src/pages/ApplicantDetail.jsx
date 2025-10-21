import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Slider,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Divider,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CardActions,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import { applicantsApi, evaluationApi, interviewApi, criteriaApi, stagesApi } from '@/lib/api'

const statusLabels = {
  pending: '保留中',
  screening: '審査中',
  interview: '面接',
  passed: '合格',
  rejected: '不合格',
}

export default function ApplicantDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [applicant, setApplicant] = useState(null)
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState(null)

  const [evaluationCriteria, setEvaluationCriteria] = useState([])
  const [criteriaList, setCriteriaList] = useState([])
  const [selectedCriteriaFile, setSelectedCriteriaFile] = useState('')
  const [overallComment, setOverallComment] = useState('')
  const [allStages, setAllStages] = useState([])

  // 最初に必要なデータをすべて読み込む
  useEffect(() => {
    const loadInitialData = async () => {
      setLoading(true)
      try {
        const [stagesRes, criteriaRes] = await Promise.all([
          stagesApi.getAll(),
          criteriaApi.getAll(),
        ])
        setAllStages(stagesRes.data)
        setCriteriaList(criteriaRes.data)
        // 応募者データもここで読み込む
        await loadApplicant()
      } catch (e) {
        console.error("初期データの読み込みに失敗しました", e)
        setError("ページの読み込みに失敗しました。")
      } finally {
        setLoading(false)
      }
    }
    loadInitialData()
  }, [id])

  // 応募者とステージ定義が読み込めたら、適切な評価基準を自動選択する
  useEffect(() => {
    if (applicant && allStages.length > 0) {
      const currentStageName = applicant.current_stage
      const stageDefinition = allStages.find(
        (s) => s.stage_name === currentStageName
      )

      if (stageDefinition) {
        setSelectedCriteriaFile(stageDefinition.criteria_filename)
      } else if (criteriaList.length > 0) {
        // 一致する定義がなければ、リストの先頭をデフォルトにする
        setSelectedCriteriaFile(criteriaList[0])
      }
    }
  }, [applicant, allStages, criteriaList])

  // 選択されたファイルまたは応募者データが変わったら、フォームの内容を更新する
  useEffect(() => {
    if (!selectedCriteriaFile || !applicant) return

    const loadAndSetCriteria = async () => {
      // 1. 保存済みの評価データを探す
      const savedEval = applicant.manual_evaluations?.find(
        (ev) => ev.criteria_filename === selectedCriteriaFile
      )

      if (savedEval) {
        // 2. 見つかったら、そのデータでフォームを復元
        setEvaluationCriteria(savedEval.evaluation_data)
        setOverallComment(savedEval.overall_comment || '')
        setError(null) // 以前のエラーをクリア
      } else {
        // 3. 見つからなければ、APIから基準の定義を読み込んで新しいフォームを表示
        try {
          const response = await criteriaApi.getByName(selectedCriteriaFile)
          setEvaluationCriteria(response.data)
          setOverallComment('') // 新しいフォームなのでコメントは空にする
          setError(null) // 以前のエラーをクリア
        } catch (e) {
          console.error('評価基準の定義の読み込みに失敗しました', e)
          setError(
            `「${selectedCriteriaFile}」の解析に失敗しました。ファイル形式を確認してください。`
          )
          setEvaluationCriteria([]) // エラー時はフォームを空にする
        }
      }
    }

    loadAndSetCriteria()
  }, [selectedCriteriaFile, applicant])

  // 評価比率
  const [skillRatio, setSkillRatio] = useState(0.2)
  const [mindsetRatio, setMindsetRatio] = useState(0.8)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    loadApplicant()
  }, [id])

  const handleSaveEvaluation = async () => {
    if (!selectedCriteriaFile) {
      alert('評価基準が選択されていません。')
      return
    }

    setIsSaving(true)
    try {
      const payload = {
        criteria_filename: selectedCriteriaFile,
        evaluation_data: evaluationCriteria,
        overall_comment: overallComment,
      }
      await evaluationApi.saveManualEvaluation(id, payload)
      alert('評価を保存しました。')
    } catch (e) {
      console.error('評価の保存に失敗しました', e)
      setError('評価の保存に失敗しました。コンソールを確認してください。')
    } finally {
      setIsSaving(false)
    }
  }

  const handleScoreChange = (index, newScore) => {
    const updatedCriteria = [...evaluationCriteria]
    updatedCriteria[index].score = newScore
    setEvaluationCriteria(updatedCriteria)
  }

  const handleMemoChange = (index, newMemo) => {
    const updatedCriteria = [...evaluationCriteria]
    updatedCriteria[index].memo = newMemo
    setEvaluationCriteria(updatedCriteria)
  }

  const loadApplicant = async () => {
    try {
      const response = await applicantsApi.getById(id)
      setApplicant(response.data)

      // 評価結果から比率を読み込み
      if (response.data.evaluation) {
        setSkillRatio(response.data.evaluation.skill_ratio || 0.2)
        setMindsetRatio(response.data.evaluation.mindset_ratio || 0.8)
      }

      setLoading(false)
    } catch (error) {
      console.error('応募者の読み込みエラー:', error)
      setError('応募者情報の読み込みに失敗しました')
      setLoading(false)
    }
  }

  const handleEvaluate = async () => {
    setProcessing(true)
    setError(null)

    try {
      await evaluationApi.evaluate(id, skillRatio, mindsetRatio)
      await loadApplicant()
      alert('評価が完了しました')
    } catch (error) {
      console.error('評価エラー:', error)
      setError('評価に失敗しました')
    } finally {
      setProcessing(false)
    }
  }

  const handleUpdateRatio = async () => {
    setProcessing(true)
    setError(null)

    try {
      await evaluationApi.updateRatio(id, skillRatio, mindsetRatio)
      await loadApplicant()
      alert('評価比率が更新されました')
    } catch (error) {
      console.error('比率更新エラー:', error)
      setError('比率の更新に失敗しました')
    } finally {
      setProcessing(false)
    }
  }

  const handleGenerateQuestions = async () => {
    setProcessing(true)
    setError(null)

    try {
      await interviewApi.generateQuestions(id, 10)
      await loadApplicant()
      alert('面接質問が生成されました')
    } catch (error) {
      console.error('質問生成エラー:', error)
      setError('質問生成に失敗しました')
    } finally {
      setProcessing(false)
    }
  }

  const handleRatioChange = (event, newValue) => {
    const newSkillRatio = newValue / 100
    const newMindsetRatio = 1 - newSkillRatio
    setSkillRatio(newSkillRatio)
    setMindsetRatio(newMindsetRatio)
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  if (!applicant) {
    return (
      <Box>
        <Alert severity="error">応募者が見つかりませんでした</Alert>
      </Box>
    )
  }

  return (
    <Box>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/applicants')}
        sx={{ mb: 2 }}
      >
        一覧に戻る
      </Button>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h4">{applicant.name}</Typography>
          <Chip label={statusLabels[applicant.status]} color="primary" />
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" color="textSecondary">
              メール
            </Typography>
            <Typography variant="body1">{applicant.email}</Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" color="textSecondary">
              電話
            </Typography>
            <Typography variant="body1">{applicant.phone || '-'}</Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* 評価比率調整 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            評価比率調整
          </Typography>
          <Box sx={{ px: 2 }}>
            <Typography gutterBottom>
              スキル評価: {(skillRatio * 100).toFixed(0)}% / マインドセット評価:{' '}
              {(mindsetRatio * 100).toFixed(0)}%
            </Typography>
            <Slider
              value={skillRatio * 100}
              onChange={handleRatioChange}
              valueLabelDisplay="auto"
              step={5}
              marks
              min={0}
              max={100}
              disabled={processing}
            />
          </Box>
          <Box sx={{ mt: 2 }}>
            <Button
              variant="contained"
              onClick={handleUpdateRatio}
              disabled={processing || !applicant.evaluation}
            >
              比率を更新して再評価
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* 評価結果 */}
      {applicant.evaluation ? (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              評価結果
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" color="textSecondary">
                  総合スコア
                </Typography>
                <Typography variant="h4">
                  {applicant.evaluation.total_score.toFixed(1)}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" color="textSecondary">
                  スキルスコア
                </Typography>
                <Typography variant="h4">
                  {applicant.evaluation.skill_score.toFixed(1)}
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" color="textSecondary">
                  マインドセットスコア
                </Typography>
                <Typography variant="h4">
                  {applicant.evaluation.mindset_score.toFixed(1)}
                </Typography>
              </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle1" gutterBottom>
              評価サマリー
            </Typography>
            <Typography variant="body1" paragraph>
              {applicant.evaluation.summary}
            </Typography>

            <Typography variant="subtitle1" gutterBottom>
              強み
            </Typography>
            <List dense>
              {applicant.evaluation.strengths.map((strength, index) => (
                <ListItem key={index}>
                  <ListItemText primary={`• ${strength}`} />
                </ListItem>
              ))}
            </List>

            <Typography variant="subtitle1" gutterBottom>
              懸念点
            </Typography>
            <List dense>
              {applicant.evaluation.concerns.map((concern, index) => (
                <ListItem key={index}>
                  <ListItemText primary={`• ${concern}`} />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      ) : (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="body1" color="textSecondary" gutterBottom>
              まだ評価されていません
            </Typography>
            <Button variant="contained" onClick={handleEvaluate} disabled={processing}>
              {processing ? <CircularProgress size={24} /> : 'AI評価を実行'}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* 一次面接評価 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6" gutterBottom sx={{ mb: 0 }}>
              一次面接評価
            </Typography>
            <FormControl size="small" sx={{ minWidth: 200 }} disabled={criteriaList.length === 0}>
              <InputLabel>評価基準</InputLabel>
              <Select
                value={selectedCriteriaFile}
                label="評価基準"
                onChange={(e) => setSelectedCriteriaFile(e.target.value)}
              >
                {criteriaList.map((fileName) => (
                  <MenuItem key={fileName} value={fileName}>
                    {fileName}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          {evaluationCriteria.map((criterion, index) => (
            <Box key={index} sx={{ mb: 3 }}>
              <Typography variant="subtitle1">{criterion.name}</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {criterion.definition}
              </Typography>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} sm={6}>
                  <Typography gutterBottom>評価スコア: {criterion.score}</Typography>
                  <Slider
                    value={criterion.score}
                    onChange={(e, newValue) => handleScoreChange(index, newValue)}
                    aria-labelledby={`slider-${index}`}
                    valueLabelDisplay="auto"
                    step={1}
                    marks
                    min={1}
                    max={5}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="評価メモ"
                    variant="outlined"
                    value={criterion.memo}
                    onChange={(e) => handleMemoChange(index, e.target.value)}
                    multiline
                    rows={2}
                  />
                </Grid>
              </Grid>
            </Box>
          ))}

          <Divider sx={{ my: 2 }} />

          <Typography variant="subtitle1" gutterBottom>
            総合コメント
          </Typography>
          <TextField
            fullWidth
            label="評価全体に関するコメント"
            variant="outlined"
            value={overallComment}
            onChange={(e) => setOverallComment(e.target.value)}
            multiline
            rows={4}
            sx={{ mb: 2 }}
          />

          <CardActions sx={{ justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleSaveEvaluation}
              disabled={isSaving}
              startIcon={isSaving ? <CircularProgress size={20} /> : null}
            >
              {isSaving ? '保存中...' : '評価を保存'}
            </Button>
          </CardActions>
        </CardContent>
      </Card>

      {/* 面接質問 */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            面接質問
          </Typography>
          {applicant.interview_questions && applicant.interview_questions.length > 0 ? (
            <List>
              {applicant.interview_questions.map((question, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={`${index + 1}. ${question}`}
                    primaryTypographyProps={{ variant: 'body1' }}
                  />
                </ListItem>
              ))}
            </List>
          ) : (
            <Box>
              <Typography variant="body1" color="textSecondary" gutterBottom>
                まだ質問が生成されていません
              </Typography>
              <Button
                variant="contained"
                onClick={handleGenerateQuestions}
                disabled={processing || !applicant.evaluation}
              >
                {processing ? <CircularProgress size={24} /> : '面接質問を生成'}
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  )
}
