import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans

class AIRoommateMatcher:
    def __init__(self, df, n_clusters):
        self.raw_df = df.copy() 
        self.encoded_df = df.copy()
        self.n_clusters = n_clusters
        
        self.feature_cols = [
            'weekday_sleep_time', 'weekday_wake_time', 'weekend_sleep_time', 'weekend_wake_time', 
            'late_night_return_frequency', 'noise_sensitivity', 'call_frequency',
            'snores', 'cleaning_frequency', 'age', 'goes_home_on_weekend', 'prefers_same_major'
        ]
        
        self._preprocess()
        self.indices = {col: i for i, col in enumerate(self.feature_cols + ['personality_extroversion', 'major_id', 'cluster_id'])}

    def _preprocess(self):
        sleep_map = {22: 0, 23: 1, 0: 2, 1: 3, 2: 4, 3: 5}
        wake_map = {6: 0, 7: 1, 8: 2, 9: 3, 10: 4, 11: 5}
        
        for col in ['weekday_sleep_time', 'weekday_wake_time', 'weekend_sleep_time', 'weekend_wake_time']:
            if col in self.encoded_df.columns:
                self.encoded_df[col] = pd.to_numeric(self.encoded_df[col], errors='coerce')
                self.encoded_df[col] = self.encoded_df[col].map(sleep_map if 'sleep' in col else wake_map)
                self.encoded_df[col] = self.encoded_df[col].fillna(self.encoded_df[col].median() if not self.encoded_df[col].isna().all() else 0)
        
        for col in ['goes_home_on_weekend', 'prefers_same_major', 'is_smoker']:
            if col in self.encoded_df.columns:
                self.encoded_df[col] = self.encoded_df[col].astype(int)
        
        le = LabelEncoder()
        self.encoded_df['major_id'] = le.fit_transform(self.encoded_df['major_name'].astype(str))
        self.encoded_df = self.encoded_df.fillna(0)

    def _apply_personalized_clustering(self, target_user_idx):
        target_user = self.raw_df.loc[target_user_idx]
        
        cluster_features = ['weekday_sleep_time', 'weekday_wake_time', 'noise_sensitivity',
                            'major_id', 'prefers_same_major', 'cleaning_frequency', 'age', 'personality_extroversion']
        weight_mapping = {
            'weekday_sleep_time': 'weight_lifestyle_rhythm',
            'weekday_wake_time': 'weight_lifestyle_rhythm',
            'noise_sensitivity': 'weight_noise',
            'major_id': 'weight_major',
            'prefers_same_major': 'weight_major',
            'cleaning_frequency': 'weight_cleaning',
            'age': 'weight_age',
            'personality_extroversion': 'weight_personality',
        }
        
        X = self.encoded_df[cluster_features].copy()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        X_weighted = pd.DataFrame(X_scaled, columns=cluster_features)
        
        # 로그인 유저 본인의 가중치 컬럼에서 값을 가져와 곱함
        for feature, weight_key in weight_mapping.items():
            user_weight = target_user[weight_key] / 10.0
            X_weighted[feature] = X_weighted[feature] * user_weight
        
        kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        cluster_ids = kmeans.fit_predict(X_weighted)
        
        self.encoded_df['cluster_id'] = cluster_ids
        self.raw_df['cluster_id'] = cluster_ids
        print(f"{target_user['name']} 유저의 가중치를 반영한 개인화 클러스터링 완료.")

    def get_custom_metric(self, dynamic_weights, noise_params):
        idx = self.indices
        w1, w2, w3 = noise_params.get('w1', 1), noise_params.get('w2', 3), noise_params.get('w3', 2)
        
        # 0 ~ 10 사이의 값으로 정규화
        w_rhythm = dynamic_weights.get('weight_lifestyle_rhythm', 50) / 10.0
        w_noise = dynamic_weights.get('weight_noise', 50) / 10.0
        w_major = dynamic_weights.get('weight_major', 50) / 10.0
        w_cleaning = dynamic_weights.get('weight_cleaning', 50) / 10.0
        w_age = dynamic_weights.get('weight_age', 50) / 10.0
        w_pers = dynamic_weights.get('weight_personality', 50) / 10.0

        def distance_func(x, y):
            dist = 0.0

            # 1. 소음 민감도
            noise_dist = w1 * abs(x[idx['noise_sensitivity']] - y[idx['noise_sensitivity']])
            noise_dist += w2 * (x[idx['snores']] * y[idx['noise_sensitivity']] + y[idx['snores']] * x[idx['noise_sensitivity']])
            noise_dist += w3 * (x[idx['call_frequency']] * y[idx['noise_sensitivity']] + y[idx['call_frequency']] * x[idx['noise_sensitivity']])
            dist += noise_dist * w_noise
            
            # 2. 취침 시간 (sleep_map이 클수록 늦게 자는 것)
            sleep_diff = x[idx['weekday_sleep_time']] - y[idx['weekday_sleep_time']]
            if sleep_diff >= 0:
                rhythm_penalty_sleep = 0.0
            else:
                rhythm_penalty_sleep = abs(sleep_diff) * 10.0  # 상대가 나보다 늦게 잠

            # 3. 기상 시간 (wake_map이 클수록 늦게 일어나는 것)
            wake_diff = x[idx['weekday_wake_time']] - y[idx['weekday_wake_time']]
            if wake_diff <= 0:
                rhythm_penalty_wake = 0.0
            else:
                rhythm_penalty_wake = abs(wake_diff) * 10.0  # 상대가 나보다 일찍 일어남
            rhythm_dist = rhythm_penalty_sleep + rhythm_penalty_wake

            # 귀가 여부 같으면 큰 페널티
            if x[idx['goes_home_on_weekend']] == y[idx['goes_home_on_weekend']]:
                rhythm_dist += 300.0 
            dist += rhythm_dist * w_rhythm
            
            # 같은 학과 선호하는 상황에서 학과 다르면 페널티
            if (x[idx['prefers_same_major']] == 1 and x[idx['major_id']] != y[idx['major_id']]): dist += 20.0 * w_major

            # 청소, 나이, 성향 페널티
            dist += abs(x[idx['cleaning_frequency']] - y[idx['cleaning_frequency']]) * w_cleaning
            dist += abs(x[idx['age']] - y[idx['age']]) * w_age
            if x[idx['personality_extroversion']] != y[idx['personality_extroversion']]:
                dist += 5.0 * w_pers
            return dist
        return distance_func

    def recommend(self, target_user_idx, noise_params, top_n=5):
        # 추천 전에 해당 유저 기준으로 클러스터링 재수행
        self._apply_personalized_clustering(target_user_idx)
        
        target_user_raw = self.raw_df.loc[target_user_idx]
        dynamic_weights = {k: target_user_raw[k] for k in ['weight_lifestyle_rhythm', 'weight_noise', 'weight_major', 'weight_cleaning', 'weight_age', 'weight_personality']}

        mask = (self.raw_df['gender'] == target_user_raw['gender']) & \
                (self.raw_df['is_smoker'] == target_user_raw['is_smoker']) & \
                (self.raw_df.index != target_user_idx)
        
        cluster_mask = mask & (self.raw_df['cluster_id'] == target_user_raw['cluster_id'])
        candidates_df = self.encoded_df[cluster_mask]
        
        if len(candidates_df) < top_n: candidates_df = self.encoded_df[mask]
        if len(candidates_df) == 0: return None

        cols_for_vector = self.feature_cols + ['personality_extroversion', 'major_id']
        X = candidates_df[cols_for_vector].values.astype(float)
        query = self.encoded_df.loc[[target_user_idx], cols_for_vector].values.astype(float)
        
        knn = NearestNeighbors(n_neighbors=min(top_n, len(candidates_df)), 
                                metric=self.get_custom_metric(dynamic_weights, noise_params), 
                                algorithm='brute')
        knn.fit(X)
        distances, indices = knn.kneighbors(query)

        res_indices = candidates_df.index[indices[0]]
        results = self.raw_df.loc[res_indices].copy()
        results['match_score'] = np.round(distances[0], 2)
        return results

    def print_cluster_stats(self, target_user_idx):
        # 통계 출력 전에도 해당 유저 기준으로 클러스터링이 되어 있어야 함
        if 'cluster_id' not in self.raw_df.columns or self.raw_df.loc[target_user_idx, 'cluster_id'] == -1:
            self._apply_personalized_clustering(target_user_idx)
            
        target = self.raw_df.loc[target_user_idx]
        print("\n[클러스터별 인원 통계 (로그인 유저 가중치 반영)]")
        print("-" * 75)

        for cluster_id in sorted(self.raw_df['cluster_id'].unique()):
            cluster_df = self.raw_df[self.raw_df['cluster_id'] == cluster_id]
            total_cnt = len(cluster_df)
            matched_cnt = cluster_df[
                (cluster_df['gender'] == target['gender']) &
                (cluster_df['is_smoker'] == target['is_smoker']) &
                (cluster_df.index != target_user_idx)
            ].shape[0]

            marker = "*" if cluster_id == target['cluster_id'] else ""
            print(f"Cluster {cluster_id:>2} | 전체: {total_cnt:>3}명 | 성별·흡연 일치: {matched_cnt:>3}명 {marker}")

# 실행
df = pd.read_csv('/workspace/mate_match/roommate_faker_data_v2.csv')
model = AIRoommateMatcher(df, n_clusters=5) 
noise_params = {'w1': 1, 'w2': 3, 'w3': 2}

target_idx = 5
model.print_cluster_stats(target_user_idx=target_idx) # 여기서 개인화 클러스터링 자동 실행
result = model.recommend(target_user_idx=target_idx, noise_params=noise_params)

if result is not None:
    target = model.raw_df.loc[target_idx]
    print(f"\n[대상자: {target['name']}] (ID: {target_idx})")
    print(f"가중치: 리듬({target['weight_lifestyle_rhythm']}), 소음({target['weight_noise']}), 전공({target['weight_major']}), 청소({target['weight_cleaning']}), 성격({target['weight_cleaning']})")
    print(f"성별: {target['gender']}, 흡연: {target['is_smoker']}, 성향: {target['personality_extroversion']}, 주말 귀가: {target['goes_home_on_weekend']}, {target['weekday_sleep_time']}시 취침, {target['weekday_wake_time']}시 기상")
    print("-" * 150)
    print(result[['name', 'age', 'gender', 'is_smoker', 'match_score', 'weekday_sleep_time', 'weekday_wake_time', 'goes_home_on_weekend', 'personality_extroversion', 'major_name']])