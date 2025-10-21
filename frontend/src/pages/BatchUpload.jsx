import { useState } from 'react'
import {
  Box,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  CircularProgress,
  Slider,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  IconButton,
} from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import DownloadIcon from '@mui/icons-material/Download'
import DeleteIcon from '@mui/icons-material/Delete'
import { batchApi, criteriaApi } from '@/lib/api'

export default function BatchUpload() {
  const [file, setFile] = useState(null)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const [criteriaFile, setCriteriaFile] = useState(null)
  const [criteriaLoading, setCriteriaLoading] = useState(false)
  const [criteriaError, setCriteriaError] = useState(null)
  const [criteriaList, setCriteriaList] = useState([])

  useEffect(() => {
    loadCriteriaFiles()
  }, [])

  const loadCriteriaFiles = async () => {
    try {
      const response = await criteriaApi.getAll()
      setCriteriaList(response.data)
    } catch (error) {
      console.error('評価基準リストの読み込みエラー:', error)
      setCriteriaError('評価基準リストの読み込みに失敗しました')
    }
  }

  // 評価比率
  const [skillRatio, setSkillRatio] = useState(0.2)
  const [mindsetRatio, setMindsetRatio] = useState(0.8)

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0]
    if (selectedFile && selectedFile.type === 'text/csv') {
      setFile(selectedFile)
      setError(null)
    } else {
      setError('CSVファイルを選択してください')
      setFile(null)
    }
  }

  const handleRatioChange = (event, newValue) => {
    const newSkillRatio = newValue / 100
    const newMindsetRatio = 1 - newSkillRatio
    setSkillRatio(newSkillRatio)
    setMindsetRatio(newMindsetRatio)
  }

  const handleCriteriaFileChange = (event) => {
    const selectedFile = event.target.files[0]
    if (selectedFile) {
      setCriteriaFile(selectedFile)
      setCriteriaError(null)
    } else {
      setCriteriaFile(null)
    }
  }

  const handleCriteriaUpload = async () => {
    if (!criteriaFile) {
      setCriteriaError('ファイルを選択してください')
      return
    }

    setCriteriaLoading(true)
    setCriteriaError(null)

    try {
      const response = await criteriaApi.uploadFile(criteriaFile)
      alert(response.data.message || '評価基準ファイルをアップロードしました')
      setCriteriaFile(null)
      loadCriteriaFiles() // リストを再読み込み
    } catch (error) {
      console.error('評価基準アップロードエラー:', error)
      setCriteriaError(
        error.response?.data?.detail || '評価基準ファイルのアップロードに失敗しました'
      )
    } finally {
      setCriteriaLoading(false)
    }
  }

  const handleDeleteCriteria = async (filename) => {
    if (window.confirm(`本当にファイル「${filename}」を削除しますか？`)) {
      try {
        await criteriaApi.deleteFile(filename)
        alert('ファイルを削除しました。')
        loadCriteriaFiles() // リストを再読み込み
      } catch (error) {
        console.error('ファイル削除エラー:', error)
        setCriteriaError(error.response?.data?.detail || 'ファイルの削除に失敗しました')
      }
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('ファイルを選択してください')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await batchApi.uploadCsv(file, skillRatio, mindsetRatio)
      setResults(response.data)
      alert('バッチ処理が完了しました')
    } catch (error) {
      console.error('アップロードエラー:', error)
      setError('バッチ処理に失敗しました')
    } finally {
      setLoading(false)
    }
  }

  const handleExportResults = async () => {
    try {
      const response = await batchApi.exportResults()
      const data = response.data.data

      // CSVダウンロード
      const csv = convertToCSV(data)
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = 'evaluation_results.csv'
      link.click()
    } catch (error) {
      console.error('エクスポートエラー:', error)
      setError('結果のエクスポートに失敗しました')
    }
  }

  const convertToCSV = (data) => {
    const headers = Object.keys(data[0]).join(',')
    const rows = data.map((row) => Object.values(row).join(',')).join('\n')
    return `${headers}\n${rows}`
  }

  return (
    <Box>
      {/* 応募者CSVバッチ処理 */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        応募者CSVバッチ処理
      </Typography>
      <Alert severity="info" sx={{ mb: 3 }}>
        応募者情報をCSVでアップロードして、一括でAI評価を実行します。
      </Alert>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* 評価比率設定 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            評価比率設定
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
              disabled={loading}
            />
          </Box>
        </CardContent>
      </Card>

      {/* ファイルアップロード */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" alignItems="center" gap={2}>
          <input
            accept=".csv"
            style={{ display: 'none' }}
            id="csv-file-upload"
            type="file"
            onChange={handleFileChange}
          />
          <label htmlFor="csv-file-upload">
            <Button variant="outlined" component="span" startIcon={<CloudUploadIcon />}>
              CSVファイルを選択
            </Button>
          </label>

          {file && (
            <Typography variant="body1" color="textSecondary">
              選択: {file.name}
            </Typography>
          )}
        </Box>

        <Box sx={{ mt: 2 }}>
          <Button
            variant="contained"
            onClick={handleUpload}
            disabled={!file || loading}
            startIcon={loading ? <CircularProgress size={20} /> : null}
          >
            {loading ? '処理中...' : 'アップロードして評価開始'}
          </Button>
        </Box>
      </Paper>

      {/* 評価基準ファイルアップロード */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        評価基準ファイルのアップロード
      </Typography>
      <Alert severity="info" sx={{ mb: 3 }}>
        評価フォームで使用する評価基準のファイル（.csv, .xlsx, .pdf, .md, .docx）をアップロードします。
      </Alert>

      {criteriaError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {criteriaError}
        </Alert>
      )}

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" alignItems="center" gap={2}>
          <input
            accept=".csv,.xlsx,.pdf,.md,.docx"
            style={{ display: 'none' }}
            id="criteria-file-upload"
            type="file"
            onChange={handleCriteriaFileChange}
          />
          <label htmlFor="criteria-file-upload">
            <Button variant="outlined" component="span" startIcon={<CloudUploadIcon />}>
              基準ファイルを選択
            </Button>
          </label>

          {criteriaFile && (
            <Typography variant="body1" color="textSecondary">
              選択: {criteriaFile.name}
            </Typography>
          )}
        </Box>

        <Box sx={{ mt: 2 }}>
          <Button
            variant="contained"
            onClick={handleCriteriaUpload}
            disabled={!criteriaFile || criteriaLoading}
            startIcon={criteriaLoading ? <CircularProgress size={20} /> : null}
          >
            {criteriaLoading ? 'アップロード中...' : '基準をアップロード'}
          </Button>
        </Box>
      </Paper>

      {/* 基準ファイル管理 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            アップロード済み評価基準
          </Typography>
          {criteriaList.length > 0 ? (
            <List dense>
              {criteriaList.map((filename) => (
                <ListItem
                  key={filename}
                  secondaryAction={
                    <IconButton
                      edge="end"
                      aria-label="delete"
                      onClick={() => handleDeleteCriteria(filename)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  }
                >
                  <ListItemText primary={filename} />
                </ListItem>
              ))}
            </List>
          ) : (
            <Typography variant="body2" color="text.secondary">
              アップロード済みのファイルはありません。
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* 結果表示 */}
      {results && (
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">処理結果</Typography>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={handleExportResults}
            >
              結果をエクスポート
            </Button>
          </Box>

          <Alert severity="success" sx={{ mb: 2 }}>
            総数: {results.total_count} | 成功: {results.success_count} | エラー:{' '}
            {results.error_count}
          </Alert>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>名前</TableCell>
                  <TableCell>メール</TableCell>
                  <TableCell>ステータス</TableCell>
                  <TableCell>スコア</TableCell>
                  <TableCell>エラー</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.results.map((result, index) => (
                  <TableRow key={index}>
                    <TableCell>{result.name}</TableCell>
                    <TableCell>{result.email}</TableCell>
                    <TableCell>
                      {result.status === 'success' ? '成功' : 'エラー'}
                    </TableCell>
                    <TableCell>
                      {result.total_score ? result.total_score.toFixed(1) : '-'}
                    </TableCell>
                    <TableCell>{result.error || '-'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}
    </Box>
  )
}
