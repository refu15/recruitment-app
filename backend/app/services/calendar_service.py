from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.utils.config import settings
import os

class CalendarService:
    def __init__(self, credentials_path: str = None):
        """
        Google Calendar APIサービス

        Args:
            credentials_path: OAuth2認証情報ファイルのパス
                            （本番環境では環境変数から読み込む）
        """
        self.credentials_path = credentials_path or settings.google_application_credentials

    def create_interview_event(
        self,
        applicant_name: str,
        applicant_email: str,
        start_time: datetime,
        duration_minutes: int = 60,
        description: str = "",
        calendar_id: str = 'primary'
    ) -> Dict[str, Any]:
        """
        面接イベントを作成

        Args:
            applicant_name: 応募者名
            applicant_email: 応募者メールアドレス
            start_time: 開始時刻
            duration_minutes: 面接時間（分）
            description: イベント詳細
            calendar_id: カレンダーID（デフォルト: primary）

        Returns:
            作成されたイベント情報
        """
        try:
            service = self._get_calendar_service()

            # 終了時刻を計算
            end_time = start_time + timedelta(minutes=duration_minutes)

            # イベントデータ
            event = {
                'summary': f'面接: {applicant_name}',
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Tokyo',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Tokyo',
                },
                'attendees': [
                    {'email': applicant_email},
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1日前
                        {'method': 'popup', 'minutes': 30},  # 30分前
                    ],
                },
            }

            # イベント作成
            created_event = service.events().insert(
                calendarId=calendar_id,
                body=event,
                sendUpdates='all'  # 招待メールを送信
            ).execute()

            return {
                'success': True,
                'event_id': created_event.get('id'),
                'event_link': created_event.get('htmlLink'),
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }

        except (HttpError, Exception) as error:
            print(f'Calendar API エラー: {error}')
            return {
                'success': False,
                'error': str(error)
            }

    def find_available_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 60,
        business_hours_start: int = 9,
        business_hours_end: int = 18,
        calendar_id: str = 'primary'
    ) -> List[Dict[str, Any]]:
        """
        空き時間スロットを検索

        Args:
            start_date: 検索開始日
            end_date: 検索終了日
            duration_minutes: 必要な時間（分）
            business_hours_start: 営業時間開始（時）
            business_hours_end: 営業時間終了（時）
            calendar_id: カレンダーID

        Returns:
            空き時間スロットのリスト
        """
        try:
            service = self._get_calendar_service()

            # 既存イベントを取得
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            # 空き時間を検索
            available_slots = []
            current_date = start_date

            while current_date < end_date:
                # 営業時間内のスロットを生成
                slot_start = current_date.replace(
                    hour=business_hours_start,
                    minute=0,
                    second=0,
                    microsecond=0
                )
                slot_end = current_date.replace(
                    hour=business_hours_end,
                    minute=0,
                    second=0,
                    microsecond=0
                )

                # 30分単位でチェック
                while slot_start + timedelta(minutes=duration_minutes) <= slot_end:
                    # このスロットが既存イベントと重複していないかチェック
                    is_available = True
                    slot_end_time = slot_start + timedelta(minutes=duration_minutes)

                    for event in events:
                        event_start = datetime.fromisoformat(
                            event['start'].get('dateTime', event['start'].get('date'))
                        )
                        event_end = datetime.fromisoformat(
                            event['end'].get('dateTime', event['end'].get('date'))
                        )

                        # 重複チェック
                        if (slot_start < event_end and slot_end_time > event_start):
                            is_available = False
                            break

                    if is_available:
                        available_slots.append({
                            'start': slot_start.isoformat(),
                            'end': slot_end_time.isoformat(),
                            'duration_minutes': duration_minutes
                        })

                    slot_start += timedelta(minutes=30)

                current_date += timedelta(days=1)

            return available_slots

        except (HttpError, Exception) as error:
            print(f'Calendar API エラー: {error}')
            return []

    def update_interview_event(
        self,
        event_id: str,
        start_time: datetime = None,
        duration_minutes: int = None,
        description: str = None,
        calendar_id: str = 'primary'
    ) -> Dict[str, Any]:
        """
        面接イベントを更新

        Args:
            event_id: イベントID
            start_time: 新しい開始時刻（オプション）
            duration_minutes: 新しい面接時間（オプション）
            description: 新しい説明（オプション）
            calendar_id: カレンダーID

        Returns:
            更新結果
        """
        try:
            service = self._get_calendar_service()

            # 既存イベント取得
            event = service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            # 更新
            if start_time:
                end_time = start_time + timedelta(
                    minutes=duration_minutes or 60
                )
                event['start'] = {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Tokyo',
                }
                event['end'] = {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Tokyo',
                }

            if description:
                event['description'] = description

            updated_event = service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()

            return {
                'success': True,
                'event_id': updated_event.get('id'),
                'event_link': updated_event.get('htmlLink')
            }

        except (HttpError, Exception) as error:
            print(f'Calendar API エラー: {error}')
            return {
                'success': False,
                'error': str(error)
            }

    def cancel_interview_event(
        self,
        event_id: str,
        calendar_id: str = 'primary'
    ) -> Dict[str, Any]:
        """
        面接イベントをキャンセル

        Args:
            event_id: イベントID
            calendar_id: カレンダーID

        Returns:
            キャンセル結果
        """
        try:
            service = self._get_calendar_service()

            service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates='all'
            ).execute()

            return {
                'success': True,
                'message': 'Event cancelled successfully'
            }

        except (HttpError, Exception) as error:
            print(f'Calendar API エラー: {error}')
            return {
                'success': False,
                'error': str(error)
            }

    def _get_calendar_service(self):
        """
        Google Calendar APIサービスを取得

        注意: 本番環境ではOAuth2フローを実装する必要があります
        現在はサービスアカウント認証を想定
        """
        if not self.credentials_path:
            raise Exception("Google Calendarの認証情報が設定されていません。")

        from google.oauth2 import service_account

        SCOPES = ['https://www.googleapis.com/auth/calendar']

        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=SCOPES
        )

        service = build('calendar', 'v3', credentials=credentials)
        return service