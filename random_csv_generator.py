import pandas as pd
from faker import Faker
import random

fake = Faker('ko_KR')

sleep_times = ['22', '23', '00', '01', '02', '03']
wake_times  = ['06', '07', '08', '09', '10', '11']

male_given_names = [
    "서준", "민준", "하준", "도윤", "시우", "지후", "준우", "유준", "건우",
    "은우", "현우", "지훈", "승현", "재윤", "시윤", "예준", "민수", "대현", "승민"
]

female_given_names = [
    "서연", "서윤", "하윤", "지우", "지민", "채원", "수아", "예린",
    "지안", "다은", "유나", "나연", "소윤", "민서", "윤서", "예은", "은서"
]

def generate_name(gender):
    last = fake.last_name()
    if gender == 'male':
        return last + random.choice(male_given_names)
    return last + random.choice(female_given_names)

def generate_student_id(yy, seq):
    return f"{yy:02d}{seq:06d}"

def generate_students(n):
    data = []
    year_seq = {yy: 0 for yy in range(17, 26)}

    genders = ['male'] * (n // 2) + ['female'] * (n // 2)
    if n % 2:
        genders.append(random.choice(['male', 'female']))
    random.shuffle(genders)

    for gender in genders:
        yy = random.randint(17, 25)
        year_seq[yy] += 1

        data.append({
            'student_id': generate_student_id(yy, year_seq[yy]),
            'name': generate_name(gender),
            'age': random.randint(20, 28),
            'gender': gender,
            'is_smoker': fake.boolean(30),

            'weekday_sleep_time': random.choice(sleep_times),
            'weekday_wake_time': random.choice(wake_times),
            'weekend_sleep_time': random.choice(sleep_times),
            'weekend_wake_time': random.choice(wake_times),
            'goes_home_on_weekend': fake.boolean(30),

            'late_night_return_frequency': random.randint(0, 7),
            'drinking_frequency': random.randint(0, 7),
            'noise_sensitivity': random.randint(1, 5),
            'call_frequency': random.randint(0, 7),
            'snores': random.choice([True, False]),

            'prefers_same_major': fake.boolean(),
            'major_name': random.choice([
                "컴퓨터공학과", "정보보호학과", "경영학부",
                "경제학과", "자유전공학부"
            ]),
            'cleaning_frequency': random.randint(0, 7),
            'personality_extroversion': random.randint(1, 5),

            'weight_lifestyle_rhythm': random.randint(0, 100),
            'weight_noise': random.randint(0, 100),
            'weight_major': random.randint(0, 100),
            'weight_cleaning': random.randint(0, 100),
            'weight_age': random.randint(0, 100),
            'weight_personality': random.randint(0, 100),

            'is_matched': False,
            'matched_room_id': None,
            'my_satisfaction_score': None,
            'partner_satisfaction_score': None,
            'cluster_id': None,
        })

    return pd.DataFrame(data)

df = generate_students(700)
df.to_csv('students_ready.csv', index=False, encoding='utf-8-sig')
