# 학사 일정 웹앱

React + Vite 웹 버전입니다. Firebase Authentication(이메일/비밀번호)과 Cloud Firestore를 사용하고, 데이터는 로그인한 사용자의 UID 아래에 저장합니다.

## 로컬 실행

1. `cp .env.example .env.local`을 실행합니다.
2. Firebase 웹 앱 설정의 값을 `.env.local`에 채웁니다.
3. `npm install` 후 `npm run dev`를 실행합니다.

Firebase 콘솔에서 이메일/비밀번호 로그인을 활성화하고 Cloud Firestore를 생성하세요. Firestore 규칙에는 이 폴더의 `firestore.rules` 내용을 배포해야 합니다.

## Vercel 배포

이 GitHub 저장소를 사용하는 Vercel 프로젝트의 **Root Directory**를 `school-calendar/web`로 설정하세요. Framework Preset은 Vite, Build Command는 `npm run build`, Output Directory는 `dist`입니다.

Vercel Project Settings → Environment Variables에 아래 변수를 등록한 다음 새 배포를 실행하세요.

- `VITE_FIREBASE_API_KEY`
- `VITE_FIREBASE_AUTH_DOMAIN`
- `VITE_FIREBASE_PROJECT_ID`
- `VITE_FIREBASE_STORAGE_BUCKET`
- `VITE_FIREBASE_MESSAGING_SENDER_ID`
- `VITE_FIREBASE_APP_ID`

Firebase Authentication의 승인된 도메인 목록에 배포된 `*.vercel.app` 도메인도 추가해야 합니다.

Firebase 웹 설정 값은 클라이언트에서 쓰는 공개 설정입니다. 데이터 접근은 Firestore 보안 규칙으로 사용자별로 제한하세요. 서비스 계정 키나 Admin SDK 비밀 키는 웹 앱에 넣지 마세요.
