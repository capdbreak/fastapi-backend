from datetime import datetime
from typing import List
from fastapi_utilities import repeat_at, repeat_every
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from os import getenv
import logging
from app.database import get_db
from app.llm import get_summaries_for_user
from app.models import User

class EmailSchema(BaseModel):
    email: List[EmailStr]

conf = ConnectionConfig(
    MAIL_USERNAME = getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = getenv("MAIL_PASSWORD"),
    MAIL_FROM = getenv("MAIL_FROM"),
    MAIL_PORT = getenv("MAIL_PORT"),
    MAIL_SERVER = getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)
logger = logging.getLogger(__name__)

def build_email_body(user_name: str, summaries: list[dict]) -> str:
    """모던하고 세련된 HTML 이메일 템플릿 생성"""
    current_date = datetime.now().strftime("%Y년 %m월 %d일")
    
    # 메인 스타일
    styles = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        
        body {
            margin: 0;
            padding: 0;
            font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f8fafc;
            line-height: 1.6;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 30px;
            text-align: center;
            color: white;
        }
        
        .header h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .header .date {
            font-size: 16px;
            opacity: 0.9;
            font-weight: 300;
        }
        
        .greeting {
            padding: 30px;
            background-color: #ffffff;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .greeting h2 {
            margin: 0;
            font-size: 20px;
            color: #2d3748;
            font-weight: 500;
        }
        
        .content {
            padding: 20px 30px;
        }
        
        .news-item {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            margin-bottom: 20px;
            padding: 25px;
            transition: transform 0.2s ease;
        }
        
        .news-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }
        
        .ticker {
            display: inline-block;
            background: linear-gradient(45deg, #4299e1, #3182ce);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 12px;
            letter-spacing: 0.5px;
        }
        
        .news-title {
            font-size: 18px;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 15px;
            line-height: 1.4;
        }
        
        .news-summary {
            color: #4a5568;
            font-size: 14px;
            line-height: 1.6;
            background-color: #f7fafc;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #4299e1;
        }
        
        .footer {
            background-color: #2d3748;
            padding: 30px;
            text-align: center;
            color: #a0aec0;
        }
        
        .footer p {
            margin: 0;
            font-size: 14px;
        }
        
        .unsubscribe {
            margin-top: 15px;
            font-size: 12px;
        }
        
        .unsubscribe a {
            color: #4299e1;
            text-decoration: none;
        }
        
        @media only screen and (max-width: 600px) {
            .container {
                margin: 0;
            }
            
            .header, .greeting, .content, .footer {
                padding-left: 20px;
                padding-right: 20px;
            }
            
            .header h1 {
                font-size: 24px;
            }
            
            .news-item {
                padding: 20px;
            }
        }
    </style>
    """
    
    # HTML 구조
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FinanceFlow 뉴스레터</title>
        {styles}
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <div class="header">
                <h1>FinanceFlow 뉴스레터</h1>
                <div class="date">{current_date}</div>
            </div>
            
            <!-- Greeting -->
            <div class="greeting">
                <h2>안녕하세요, {user_name}님! 👋</h2>
                <p style="margin: 10px 0 0 0; color: #718096;">오늘도 중요한 뉴스를 요약해서 전해드립니다.</p>
            </div>
            
            <!-- Content -->
            <div class="content">
    """
    
    # 뉴스 아이템들 추가
    for item in summaries:
        html_content += f"""
                <div class="news-item">
                    <div class="ticker">{item['ticker']}</div>
                    <div class="news-title"><a href="{item['real_url']}">{item['title']}</a></div>
                    <div class="news-summary">
                        <strong>📝 요약:</strong><br>
                        {item['summary']}
                    </div>
                </div>
        """
    
    # Footer 추가
    html_content += f"""
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <p>📊 <strong>FinanceFlow 뉴스레터</strong></p>
                <p>매일 아침 신선한 뉴스를 전해드립니다</p>
                <div class="unsubscribe">
                    <p>수신 거부를 원하시면 <a href="mailto:{getenv('MAIL_FROM')}?subject=Unsubscribe">여기를 클릭하세요</a>.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

db = get_db()

#@repeat_at(cron="0 0 * * *", raise_exceptions=True)
@repeat_every(seconds=60 * 60 * 24, raise_exceptions=True)
async def send_newsletter():
    """
    사용자들에게 개인화된 뉴스레터를 발송합니다.
    """
    db_session = next(db)
    user_list = db_session.query(User).filter(User.email_opt_in).all()

    for user in user_list:
        try:
            summaries = await get_summaries_for_user(user, db_session)
            if summaries:
                html_body = build_email_body(user.name, summaries)
                fm = FastMail(conf)
                message = MessageSchema(
                    subject=f'{datetime.now().strftime("%m월 %d일")} FinanceFlow 뉴스레터',
                    recipients=[user.email],
                    body=html_body,
                    subtype=MessageType.html,
                )
                await fm.send_message(message)
                logger.info(f"Newsletter sent successfully to {user.email}")
            else:
                logger.info(f"No summaries available for user {user.email}")
                
        except Exception as e:
            logger.error(f"Failed to send newsletter to {user.email}: {str(e)}")
