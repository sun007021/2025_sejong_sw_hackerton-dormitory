import pandas as pd
from faker import Faker
import random

# 한국어 설정   
fake = Faker('ko_KR')

# 성별별 이름 리스트
male_given_names = [
    "서준", "민준", "하준", "도윤", "시우", "지후", "준우", "유준", "건우",
    "은우", "현우", "지훈", "승현", "재윤", "시윤", "예준", "민수", "대현", "승민"
]

female_given_names = [
    "서연", "서윤", "하윤", "지우", "지민", "채원", "수아", "예린",
    "지안", "다은", "유나", "나연", "소윤", "민서", "윤서", "예은", "은서"
]

def generate_modern_korean_name(gender):
    last_name = fake.last_name()
    if gender == '남':
        return last_name + random.choice(male_given_names)
    else:
        return last_name + random.choice(female_given_names)

def generate_roommate_data(num_users):
    data = []
    sleep_times = ['22', '23', '00', '01', '02', '03']
    wake_times = ['06', '07', '08', '09', '10', '11']

    majors = [
        "국어국문학과", "국제학부 영어데이터융합전공", "국제학부 일어일문학전공",
        "국제학부 중국통상학전공", "역사학과", "교육학과",
        "글로벌인재학부 한국언어문화전공", "글로벌인재학부 국제통상전공",
        "글로벌인재학부 국제협력전공", "행정학과", "미디어커뮤니케이션학과",
        "법학과", "경영학부", "경제학과",
        "호텔관광외식경영학부 호텔관광경영학전공",
        "호텔관광외식경영학부 외식경영학전공",
        "호텔외식관광프랜차이즈경영학과", "글로벌조리학과",
        "수학통계학과", "물리천문학과", "화학과",
        "생명시스템학부 식품생명공학전공",
        "생명시스템학부 바이오융합공학전공",
        "생명시스템학부 바이오산업자원공학전공",
        "스마트생명산업융합학과", "AI융합전자공학과",
        "반도체시스템공학과", "컴퓨터공학과", "정보보호학과",
        "콘텐츠소프트웨어학과", "지능정보융합학과",
        "인공지능데이터사이언스학과", "AI로봇학과",
        "창의소프트학부 디자인이노베이션전공",
        "창의소프트학부 만화애니메이션텍전공",
        "사이버국방학과", "건축공학과", "건축학과",
        "건설환경공학과", "환경융합공학과",
        "지구자원시스템공학과", "기계공학과",
        "우주항공시스템학부 우주항공공학전공",
        "우주항공시스템학부 항공시스템공학전공",
        "우주항공시스템학부 지능형드론융합전공",
        "나노신소재공학과", "양자원자력공학과",
        "국방시스템공학과", "회화과", "패션디자인학과",
        "음악과", "체육학과", "무용과", "영화예술학과",
        "자유전공학부"
    ]

    # 성비 1:1 생성
    half = num_users // 2
    genders = ['남'] * half + ['여'] * half

    # 홀수 명이면 마지막 1명 랜덤 추가
    if num_users % 2 == 1:
        genders.append(random.choice(['남', '여']))
    random.shuffle(genders)

    for gender in genders:
        goes_home_on_weekend = fake.boolean(chance_of_getting_true=30)

        user = {
            'name': generate_modern_korean_name(gender),
            'age': random.randint(20, 28),
            'gender': gender,
            'is_smoker': fake.boolean(chance_of_getting_true=30),

            # 생활 리듬
            'weekday_sleep_time': random.choice(sleep_times),
            'weekday_wake_time': random.choice(wake_times),
            'weekend_sleep_time': None if goes_home_on_weekend else random.choice(sleep_times),
            'weekend_wake_time': None if goes_home_on_weekend else random.choice(wake_times),
            'goes_home_on_weekend': goes_home_on_weekend,

            # 수치형 데이터
            'late_night_return_frequency': random.randint(1, 5) if goes_home_on_weekend else random.randint(0, 7),
            'drinking_frequency': random.randint(0, 5) if goes_home_on_weekend else random.randint(0, 7),
            'noise_sensitivity': random.randint(1, 5),
            'call_frequency': random.randint(1, 7),
            'snores': random.choice([0, 1]),

            # 전공 및 기타
            'prefers_same_major': fake.boolean(),
            'major_name': random.choice(majors),
            'cleaning_frequency': random.randint(1, 7),
            'personality_extroversion': random.choice([0, 1]),

            # 가중치
            'weight_lifestyle_rhythm': random.randint(0, 100),
            'weight_noise': random.randint(0, 100),
            'weight_major': random.randint(0, 100),
            'weight_cleaning': random.randint(0, 100),
            'weight_age': random.randint(0, 100),
            'weight_personality': random.randint(0, 100),
        }

        data.append(user)

    return pd.DataFrame(data)

# 데이터 생성 및 저장
df = generate_roommate_data(700) # 700명

df.insert(0, '#', range(1, len(df) + 1))
df.insert(1, 'id', '')
df.insert(2, 'student_id', '')
df['is_matched'] = ''
df['matched_room_id'] = ''
df['created_at'] = ''
df['updated_at'] = ''

df.to_csv('./roommate_faker_data_v2.csv', index=False, encoding='utf-8-sig')

print("Faker로 생성된 데이터 샘플:")
print(df[['name', 'gender', 'goes_home_on_weekend', 'weekday_sleep_time', 'weekday_wake_time', 'major_name']].head())
