import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Button,
  TextField,
  MenuItem,
  CircularProgress,
} from '@mui/material'
import VisibilityIcon from '@mui/icons-material/Visibility'
import AddIcon from '@mui/icons-material/Add'
import { applicantsApi } from '@/lib/api'

const statusColors = {
  pending: 'warning',
  screening: 'info',
  interview: 'primary',
  passed: 'success',
  rejected: 'error',
}

const statusLabels = {
  pending: '保留中',
  screening: '審査中',
  interview: '面接',
  passed: '合格',
  rejected: '不合格',
}

export default function ApplicantsList() {
  const navigate = useNavigate()
  const [applicants, setApplicants] = useState([])
  const [filteredApplicants, setFilteredApplicants] = useState([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadApplicants()
  }, [])

  useEffect(() => {
    filterApplicants()
  }, [applicants, statusFilter, searchQuery])

  const loadApplicants = async () => {
    try {
      const response = await applicantsApi.getAll()
      setApplicants(response.data)
      setLoading(false)
    } catch (error) {
      console.error('応募者の読み込みエラー:', error)
      setLoading(false)
    }
  }

  const filterApplicants = () => {
    let filtered = applicants

    // ステータスフィルター
    if (statusFilter !== 'all') {
      filtered = filtered.filter((a) => a.status === statusFilter)
    }

    // 検索クエリ
    if (searchQuery) {
      filtered = filtered.filter(
        (a) =>
          a.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          a.email.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    setFilteredApplicants(filtered)
  }

  const getScore = (applicant) => {
    if (applicant.evaluation && applicant.evaluation.total_score) {
      return applicant.evaluation.total_score.toFixed(1)
    }
    return '-'
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">応募者一覧</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/applicants/new')}
        >
          新規応募者
        </Button>
      </Box>

      <Box display="flex" gap={2} mb={3}>
        <TextField
          label="検索"
          variant="outlined"
          size="small"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          sx={{ minWidth: 300 }}
        />
        <TextField
          select
          label="ステータス"
          size="small"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          sx={{ minWidth: 200 }}
        >
          <MenuItem value="all">すべて</MenuItem>
          <MenuItem value="pending">保留中</MenuItem>
          <MenuItem value="screening">審査中</MenuItem>
          <MenuItem value="interview">面接</MenuItem>
          <MenuItem value="passed">合格</MenuItem>
          <MenuItem value="rejected">不合格</MenuItem>
        </TextField>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>名前</TableCell>
              <TableCell>メール</TableCell>
              <TableCell>ステータス</TableCell>
              <TableCell>総合スコア</TableCell>
              <TableCell>作成日</TableCell>
              <TableCell>操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredApplicants.map((applicant) => (
              <TableRow key={applicant.id} hover>
                <TableCell>{applicant.name}</TableCell>
                <TableCell>{applicant.email}</TableCell>
                <TableCell>
                  <Chip
                    label={statusLabels[applicant.status]}
                    color={statusColors[applicant.status]}
                    size="small"
                  />
                </TableCell>
                <TableCell>{getScore(applicant)}</TableCell>
                <TableCell>
                  {new Date(applicant.created_at).toLocaleDateString('ja-JP')}
                </TableCell>
                <TableCell>
                  <IconButton
                    color="primary"
                    onClick={() => navigate(`/applicants/${applicant.id}`)}
                  >
                    <VisibilityIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {filteredApplicants.length === 0 && (
        <Box textAlign="center" py={4}>
          <Typography color="textSecondary">
            応募者が見つかりませんでした
          </Typography>
        </Box>
      )}
    </Box>
  )
}
