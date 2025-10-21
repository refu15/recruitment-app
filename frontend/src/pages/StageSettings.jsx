import { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Paper,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Alert,
} from '@mui/material'
import { stagesApi, criteriaApi } from '@/lib/api.js'

export default function StageSettings() {
  const [stages, setStages] = useState([])
  const [criteriaFiles, setCriteriaFiles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // 新規ステージ用state
  const [newStageName, setNewStageName] = useState('')
  const [newCriteriaFile, setNewCriteriaFile] = useState('')
  const [newOrder, setNewOrder] = useState(1)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [stagesRes, criteriaRes] = await Promise.all([
        stagesApi.getAll(),
        criteriaApi.getAll(),
      ])
      setStages(stagesRes.data)
      setCriteriaFiles(criteriaRes.data)
      setNewOrder(stagesRes.data.length + 1) // 次の順序を自動設定
    } catch (err) {
      console.error("データ読み込みエラー:", err)
      setError("ステージ情報または評価基準ファイルの読み込みに失敗しました。")
    } finally {
      setLoading(false)
    }
  }

  const handleAddStage = async () => {
    if (!newStageName || !newCriteriaFile || !newOrder) {
      alert('すべての項目を入力してください。')
      return
    }
    setIsSubmitting(true)
    try {
      await stagesApi.create({
        stage_name: newStageName,
        criteria_filename: newCriteriaFile,
        order: parseInt(newOrder, 10),
      })
      // フォームをリセットして再読み込み
      setNewStageName('')
      setNewCriteriaFile('')
      fetchData()
    } catch (err) {
      console.error("ステージ追加エラー:", err)
      setError("ステージの追加に失敗しました。")
    } finally {
      setIsSubmitting(false)
    }
  }

  if (loading) {
    return <CircularProgress />
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        選考ステージ設定
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* ステージ一覧 */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>現在のステージ</Typography>
        <List dense>
          {stages.map((stage) => (
            <ListItem key={stage.id}>
              <ListItemText 
                primary={`${stage.order}. ${stage.stage_name}`}
                secondary={`使用基準: ${stage.criteria_filename}`}
              />
            </ListItem>
          ))}
        </List>
      </Paper>

      {/* ステージ追加 */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>新しいステージを追加</Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <TextField
            label="順序"
            type="number"
            value={newOrder}
            onChange={(e) => setNewOrder(e.target.value)}
            sx={{ width: '100px' }}
          />
          <TextField
            label="ステージ名"
            value={newStageName}
            onChange={(e) => setNewStageName(e.target.value)}
            fullWidth
          />
          <FormControl fullWidth>
            <InputLabel>評価基準ファイル</InputLabel>
            <Select
              value={newCriteriaFile}
              label="評価基準ファイル"
              onChange={(e) => setNewCriteriaFile(e.target.value)}
            >
              {criteriaFiles.map((file) => (
                <MenuItem key={file} value={file}>
                  {file}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Button 
            variant="contained"
            onClick={handleAddStage}
            disabled={isSubmitting}
          >
            {isSubmitting ? <CircularProgress size={24} /> : '追加'}
          </Button>
        </Box>
      </Paper>
    </Box>
  )
}
