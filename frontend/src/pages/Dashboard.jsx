import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  CircularProgress,
} from '@mui/material'
import PeopleIcon from '@mui/icons-material/People'
import AssessmentIcon from '@mui/icons-material/Assessment'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty'
import { applicantsApi } from '../lib/api'

export default function Dashboard() {
  const navigate = useNavigate()
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    screening: 0,
    interview: 0,
    passed: 0,
    rejected: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const response = await applicantsApi.getAll()
      const applicants = response.data

      const stats = {
        total: applicants.length,
        pending: applicants.filter((a) => a.status === 'pending').length,
        screening: applicants.filter((a) => a.status === 'screening').length,
        interview: applicants.filter((a) => a.status === 'interview').length,
        passed: applicants.filter((a) => a.status === 'passed').length,
        rejected: applicants.filter((a) => a.status === 'rejected').length,
      }

      setStats(stats)
      setLoading(false)
    } catch (error) {
      console.error('統計の読み込みエラー:', error)
      setLoading(false)
    }
  }

  const StatCard = ({ title, value, icon, color }) => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography color="textSecondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4">{value}</Typography>
          </Box>
          <Box sx={{ color }}>{icon}</Box>
        </Box>
      </CardContent>
    </Card>
  )

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        ダッシュボード
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="総応募者数"
            value={stats.total}
            icon={<PeopleIcon fontSize="large" />}
            color="primary.main"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="保留中"
            value={stats.pending}
            icon={<HourglassEmptyIcon fontSize="large" />}
            color="warning.main"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="審査中"
            value={stats.screening}
            icon={<AssessmentIcon fontSize="large" />}
            color="info.main"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="合格"
            value={stats.passed}
            icon={<CheckCircleIcon fontSize="large" />}
            color="success.main"
          />
        </Grid>
      </Grid>

      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" gutterBottom>
          クイックアクション
        </Typography>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item>
            <Button
              variant="contained"
              onClick={() => navigate('/applicants')}
            >
              応募者一覧を表示
            </Button>
          </Grid>
          <Grid item>
            <Button
              variant="outlined"
              onClick={() => navigate('/batch')}
            >
              CSVバッチ処理
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Box>
  )
}
