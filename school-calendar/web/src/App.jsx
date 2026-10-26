import { useEffect, useMemo, useState } from 'react'
import {
  addDoc, collection, deleteDoc, doc, onSnapshot, updateDoc,
} from 'firebase/firestore'
import {
  createUserWithEmailAndPassword, onAuthStateChanged,
  sendPasswordResetEmail, signInWithEmailAndPassword, signOut,
} from 'firebase/auth'
import {
  AlertCircle, ArrowLeft, ArrowRight, CalendarDays, Check, Clock3,
  LogOut, Plus, Search, Trash2, X,
} from 'lucide-react'
import { auth, db, firebaseReady } from './firebase'

const EMPTY_FORM = {
  title: '', date: '', time: '09:00', type: '기타',
  alert_time: 'none', repeat_type: 'none', description: '',
}
const TYPES = ['시험', '과제', '행사', '기타']
const ALERTS = [
  ['none', '알림 없음'], ['1day', '하루 전'], ['3day', '3일 전'], ['1week', '일주일 전'],
]
const REPEATS = [
  ['none', '반복 없음'], ['weekly', '매주'], ['yearly', '매년'],
]

function dateKey(date) {
  return [date.getFullYear(), String(date.getMonth() + 1).padStart(2, '0'), String(date.getDate()).padStart(2, '0')].join('-')
}

function getWeek(date) {
  const monday = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  monday.setDate(monday.getDate() - ((monday.getDay() + 6) % 7))
  return Array.from({ length: 7 }, (_, index) => {
    const day = new Date(monday)
    day.setDate(monday.getDate() + index)
    return day
  })
}

function describeFirebaseError(error) {
  const messages = {
    'auth/email-already-in-use': '이미 가입된 이메일입니다.',
    'auth/invalid-credential': '이메일 또는 비밀번호를 확인해 주세요.',
    'auth/invalid-email': '이메일 형식이 올바르지 않습니다.',
    'auth/weak-password': '비밀번호는 6자 이상 입력해 주세요.',
    'auth/too-many-requests': '요청이 잠시 제한됐습니다. 잠시 후 다시 시도해 주세요.',
  }
  return messages[error.code] || error.message || '요청을 처리하지 못했습니다.'
}

function AuthPanel() {
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  async function submit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    setNotice('')
    try {
      if (mode === 'register') await createUserWithEmailAndPassword(auth, email.trim(), password)
      else await signInWithEmailAndPassword(auth, email.trim(), password)
    } catch (authError) {
      setError(describeFirebaseError(authError))
    } finally {
      setBusy(false)
    }
  }

  async function resetPassword() {
    if (!email.trim()) {
      setError('비밀번호 재설정 링크를 받을 이메일을 먼저 입력해 주세요.')
      return
    }
    try {
      await sendPasswordResetEmail(auth, email.trim())
      setError('')
      setNotice('비밀번호 재설정 메일을 보냈습니다.')
    } catch (authError) {
      setError(describeFirebaseError(authError))
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-card">
        <div className="brand-mark"><CalendarDays size={20} /></div>
        <p className="eyebrow">SCHOOL PLANNER</p>
        <h1>학사 일정을 한곳에</h1>
        <p className="auth-copy">로그인하면 웹과 데스크톱에서 같은 일정을 볼 수 있어요.</p>
        <form onSubmit={submit} className="auth-form">
          <label>이메일<input type="email" autoComplete="email" required value={email} onChange={e => setEmail(e.target.value)} placeholder="name@example.com" /></label>
          <label>비밀번호<input type="password" autoComplete={mode === 'register' ? 'new-password' : 'current-password'} minLength="6" required value={password} onChange={e => setPassword(e.target.value)} placeholder="6자 이상" /></label>
          {error && <p className="form-error">{error}</p>}
          {notice && <p className="form-notice">{notice}</p>}
          <button className="primary-button full-button" disabled={busy}>{busy ? '처리 중…' : mode === 'register' ? '계정 만들기' : '로그인'}</button>
        </form>
        <div className="auth-links">
          {mode === 'login' && <button className="text-button" onClick={resetPassword}>비밀번호 찾기</button>}
          <button className="text-button" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); setNotice('') }}>
            {mode === 'login' ? '처음 오셨나요? 회원가입' : '이미 계정이 있나요? 로그인'}
          </button>
        </div>
      </section>
    </main>
  )
}

function ScheduleDialog({ initial, onClose, onSave, onDelete }) {
  const [form, setForm] = useState(initial || { ...EMPTY_FORM, date: dateKey(new Date()) })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const editing = Boolean(initial?.id)

  function setField(name, value) {
    setForm(current => ({ ...current, [name]: value }))
  }

  async function submit(event) {
    event.preventDefault()
    if (!form.title.trim() || !form.date) {
      setError('제목과 날짜를 입력해 주세요.')
      return
    }
    setBusy(true)
    setError('')
    try {
      await onSave({ ...form, title: form.title.trim(), description: form.description.trim() })
      onClose()
    } catch (saveError) {
      setError(describeFirebaseError(saveError))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={event => { if (event.target === event.currentTarget) onClose() }}>
      <section className="schedule-dialog" role="dialog" aria-modal="true" aria-labelledby="dialog-title">
        <header className="dialog-heading"><div><p className="eyebrow">SCHEDULE</p><h2 id="dialog-title">{editing ? '일정 수정' : '새 일정'}</h2></div><button className="icon-button" onClick={onClose} aria-label="닫기"><X size={18} /></button></header>
        <form onSubmit={submit} className="schedule-form">
          <label className="wide-field">제목<input autoFocus required value={form.title} onChange={e => setField('title', e.target.value)} placeholder="예: 중간고사 수학" /></label>
          <label>날짜<input type="date" required value={form.date} onChange={e => setField('date', e.target.value)} /></label>
          <label>시간<input type="time" value={form.time} onChange={e => setField('time', e.target.value)} /></label>
          <label>유형<select value={form.type} onChange={e => setField('type', e.target.value)}>{TYPES.map(type => <option key={type}>{type}</option>)}</select></label>
          <label>알림<select value={form.alert_time} onChange={e => setField('alert_time', e.target.value)}>{ALERTS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
          <label>반복<select value={form.repeat_type} onChange={e => setField('repeat_type', e.target.value)}>{REPEATS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
          <label className="wide-field">메모<textarea rows="3" value={form.description} onChange={e => setField('description', e.target.value)} placeholder="준비물이나 참고할 내용을 적어두세요." /></label>
          {error && <p className="form-error wide-field">{error}</p>}
          <footer className="dialog-actions">
            {editing && <button type="button" className="danger-button" onClick={async () => { setBusy(true); try { await onDelete(form.id); onClose() } catch (deleteError) { setError(describeFirebaseError(deleteError)); setBusy(false) } }}><Trash2 size={15} />삭제</button>}
            <span className="action-spacer" />
            <button type="button" className="secondary-button" onClick={onClose}>취소</button>
            <button className="primary-button" disabled={busy}><Check size={15} />{busy ? '저장 중…' : '저장'}</button>
          </footer>
        </form>
      </section>
    </div>
  )
}

function Agenda({ user }) {
  const [selectedDate, setSelectedDate] = useState(() => new Date())
  const [schedules, setSchedules] = useState([])
  const [search, setSearch] = useState('')
  const [dialog, setDialog] = useState(null)
  const [loading, setLoading] = useState(true)
  const [dataError, setDataError] = useState('')
  const week = useMemo(() => getWeek(selectedDate), [selectedDate])
  const start = dateKey(week[0])
  const end = dateKey(week[6])

  useEffect(() => {
    setLoading(true)
    const schedulesRef = collection(db, 'users', user.uid, 'schedules')
    return onSnapshot(schedulesRef, snapshot => {
      setSchedules(snapshot.docs.map(item => ({ id: item.id, ...item.data() })))
      setDataError('')
      setLoading(false)
    }, error => {
      setDataError(error.message)
      setLoading(false)
    })
  }, [user.uid])

  const visible = schedules
    .filter(schedule => schedule.date >= start && schedule.date <= end)
    .filter(schedule => !search || schedule.title?.toLocaleLowerCase().includes(search.toLocaleLowerCase()))
    .sort((a, b) => a.date.localeCompare(b.date) || (a.time || '00:00').localeCompare(b.time || '00:00'))

  async function saveSchedule(schedule) {
    const { id, ...data } = schedule
    const ref = collection(db, 'users', user.uid, 'schedules')
    if (id) await updateDoc(doc(db, 'users', user.uid, 'schedules', id), data)
    else await addDoc(ref, data)
  }

  async function deleteSchedule(id) {
    await deleteDoc(doc(db, 'users', user.uid, 'schedules', id))
  }

  const monthLabel = new Intl.DateTimeFormat('ko-KR', { year: 'numeric', month: 'long' }).format(selectedDate)
  const weekLabel = `${new Intl.DateTimeFormat('ko-KR', { month: 'long', day: 'numeric' }).format(week[0])} – ${new Intl.DateTimeFormat('ko-KR', { month: 'long', day: 'numeric' }).format(week[6])}`

  function moveWeek(amount) {
    setSelectedDate(current => {
      const next = new Date(current)
      next.setDate(next.getDate() + amount * 7)
      return next
    })
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-row"><div className="brand-mark small"><CalendarDays size={17} /></div><span>학사 일정</span></div>
        <div className="mini-calendar">
          <div className="mini-calendar-header"><button className="icon-button" onClick={() => setSelectedDate(new Date(selectedDate.getFullYear(), selectedDate.getMonth() - 1, 1))} aria-label="이전 달"><ArrowLeft size={15} /></button><strong>{monthLabel}</strong><button className="icon-button" onClick={() => setSelectedDate(new Date(selectedDate.getFullYear(), selectedDate.getMonth() + 1, 1))} aria-label="다음 달"><ArrowRight size={15} /></button></div>
          <div className="month-grid weekday-row">{'월화수목금토일'.split('').map((day, index) => <span className={index > 4 ? 'weekend' : ''} key={day}>{day}</span>)}</div>
          <div className="month-grid">
            {(() => {
              const first = new Date(selectedDate.getFullYear(), selectedDate.getMonth(), 1)
              const offset = (first.getDay() + 6) % 7
              const cells = Array.from({ length: 42 }, (_, index) => {
                const day = new Date(first)
                day.setDate(index - offset + 1)
                const selected = dateKey(day) === dateKey(selectedDate)
                const outside = day.getMonth() !== selectedDate.getMonth()
                const hasSchedule = schedules.some(item => item.date === dateKey(day))
                return <button key={dateKey(day)} className={`day-cell ${selected ? 'selected' : ''} ${outside ? 'outside' : ''} ${hasSchedule ? 'has-event' : ''}`} onClick={() => setSelectedDate(day)}>{day.getDate()}</button>
              })
              return cells
            })()}
          </div>
        </div>
        <button className="today-link" onClick={() => setSelectedDate(new Date())}>오늘로 이동</button>
        <div className="sidebar-search"><label htmlFor="schedule-search">일정 검색</label><div className="search-box"><Search size={15} /><input id="schedule-search" value={search} onChange={e => setSearch(e.target.value)} placeholder="제목 검색" /></div></div>
        <div className="profile-card"><div className="avatar">{user.email?.[0]?.toUpperCase() || 'S'}</div><div className="profile-copy"><strong>{user.email}</strong><span>동기화 중인 계정</span></div><button className="icon-button" onClick={() => signOut(auth)} aria-label="로그아웃"><LogOut size={15} /></button></div>
      </aside>

      <main className="agenda-page">
        <header className="page-header"><div className="header-titles"><p className="eyebrow">WEEKLY AGENDA</p><h1>{weekLabel}</h1><p className="page-subtitle">이번 주 일정이 시간순으로 정리되어 있어요.</p></div><div className="header-actions"><button className="secondary-button today-button" onClick={() => setSelectedDate(new Date())}>오늘</button><button className="icon-button nav-button" onClick={() => moveWeek(-1)} aria-label="이전 주"><ArrowLeft size={17} /></button><button className="icon-button nav-button" onClick={() => moveWeek(1)} aria-label="다음 주"><ArrowRight size={17} /></button><button className="primary-button add-button" onClick={() => setDialog({ ...EMPTY_FORM, date: dateKey(selectedDate) })}><Plus size={17} />일정 등록</button></div></header>
        <div className="week-strip">{week.map((day, index) => {
          const today = dateKey(day) === dateKey(new Date())
          const chosen = dateKey(day) === dateKey(selectedDate)
          return <button key={dateKey(day)} className={`week-day ${today ? 'today' : ''} ${chosen ? 'chosen' : ''}`} onClick={() => setSelectedDate(day)}><span>{['월', '화', '수', '목', '금', '토', '일'][index]}</span><strong>{day.getDate()}</strong><i>{schedules.some(item => item.date === dateKey(day)) ? '•' : ''}</i></button>
        })}</div>
        {dataError && <div className="inline-error"><AlertCircle size={16} /> 일정을 불러오지 못했습니다. Firestore 규칙과 설정을 확인해 주세요. <span>{dataError}</span></div>}
        <section className="agenda-list" aria-live="polite">
          {loading ? <div className="empty-state">일정을 불러오는 중…</div> : visible.length === 0 ? <div className="empty-state"><div className="empty-icon"><CalendarDays size={21} /></div><strong>{search ? '검색 결과가 없어요' : '이번 주는 비어 있어요'}</strong><span>{search ? '다른 제목으로 검색해 보세요.' : '일정을 등록해 한 주를 계획해 보세요.'}</span><button className="secondary-button" onClick={() => setDialog({ ...EMPTY_FORM, date: dateKey(selectedDate) })}><Plus size={15} />첫 일정 등록</button></div> : week.map(day => {
            const dayKey = dateKey(day)
            const items = visible.filter(item => item.date === dayKey)
            if (!items.length) return null
            return <section className="day-section" key={dayKey}>
              <header className="day-heading"><div className="day-number">{day.getDate()}</div><div><strong>{new Intl.DateTimeFormat('ko-KR', { weekday: 'long', month: 'long', day: 'numeric' }).format(day)}</strong><span>{items.length}개 일정</span></div></header>
              <div className="day-events">{items.map(item => <button className="event-card" key={item.id} onClick={() => setDialog(item)}><span className="event-time"><Clock3 size={14} />{item.time || '하루 종일'}</span><span className="event-color" /><span className="event-content"><strong>{item.title}</strong><span className="event-meta"><em>{item.type || '기타'}</em>{item.alert_time && item.alert_time !== 'none' && <em>{ALERTS.find(([value]) => value === item.alert_time)?.[1] || item.alert_time}</em>}{item.repeat_type && item.repeat_type !== 'none' && <em>{REPEATS.find(([value]) => value === item.repeat_type)?.[1] || item.repeat_type}</em>}</span>{item.description && <span className="event-note">{item.description}</span>}</span><ArrowRight className="event-arrow" size={16} /></button>)}</div>
            </section>
          })}
        </section>
      </main>
      {dialog !== null && <ScheduleDialog initial={dialog} onClose={() => setDialog(null)} onSave={saveSchedule} onDelete={deleteSchedule} />}
    </div>
  )
}

function FirebaseSetup() {
  return <main className="setup-shell"><section className="setup-card"><div className="brand-mark"><AlertCircle size={20} /></div><p className="eyebrow">ONE LAST SETUP</p><h1>Firebase 설정이 필요해요</h1><p>웹 배포는 준비됐지만, 일정 저장소를 연결하려면 Firebase 프로젝트 설정을 Vercel에 등록해야 합니다.</p><ol><li>Firebase 콘솔에서 웹 앱을 추가하고 Authentication의 이메일/비밀번호 로그인을 켭니다.</li><li>Cloud Firestore를 만들고 저장소의 <code>firestore.rules</code> 규칙을 배포합니다.</li><li>Vercel의 Environment Variables에 <code>VITE_FIREBASE_*</code> 값을 등록한 뒤 Redeploy를 눌러 주세요.</li></ol><a href="https://console.firebase.google.com/" target="_blank" rel="noreferrer">Firebase 콘솔 열기 <ArrowRight size={15} /></a></section></main>
}

export default function App() {
  const [user, setUser] = useState(undefined)

  useEffect(() => {
    if (!firebaseReady) return undefined
    return onAuthStateChanged(auth, setUser)
  }, [])

  if (!firebaseReady) return <FirebaseSetup />
  if (user === undefined) return <main className="loading-screen">학사 일정을 준비하고 있어요…</main>
  return user ? <Agenda user={user} /> : <AuthPanel />
}
