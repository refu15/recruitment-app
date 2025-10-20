import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'

import Layout from './components/Layout'
import ApplicantsList from './pages/ApplicantsList'
import ApplicantDetail from './pages/ApplicantDetail'
import BatchUpload from './pages/BatchUpload'
import Dashboard from './pages/Dashboard'
import StageSettings from './pages/StageSettings'

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
})

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/applicants" element={<ApplicantsList />} />
            <Route path="/applicants/:id" element={<ApplicantDetail />} />
            <Route path="/batch" element={<BatchUpload />} />
            <Route path="/settings" element={<StageSettings />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  )
}

export default App
